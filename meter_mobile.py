#!/usr/bin/python
'''Script to read utility meter transmissions, log those from specified meters
to a disk file, and to display recent readings on a 2-line USB display.
Created for Marco Castillo's Enstar project.

This script assumes the RTL-SDR Software Defined Radio is based on R820T2 tuner and 
RTL2832U chips.

This script assumes that the program rtl_tcp is already running. (I tried starting
it within this script, but it then captured keystrokes such as Ctrl-C.).
'''
import subprocess
import signal
import sys
import os
import time
import logging
import threading
import config_logging

# Constants for the Program
ERROR_LOG_FILE = '/var/log/meter_mobile.log'  # error log file
RTLAMR_PATH = '/home/pi/gocode/bin/rtlamr'    # path to rtlamr program
METER_ID_FILE = '/boot/meter_mobile/meters.txt'   # has list of meter IDs, one per line
# files to write the readings into
READING_FILES = ['/boot/meter_mobile/readings.txt', '/home/pi/readings.txt']

def display(text):
    """Displays 'text' on the USB connected display; lines are delimited
    by newline characters.  The display is first cleared before displaying
    the new message.
    """
    print(text)

def shutdown(signum, frame):
    '''Kills the external processes that were started by this script
    '''
    # Hard kill these processes and I have found them difficult to kill with SIGTERM
    subprocess.call('/usr/bin/pkill -9 rtlamr', shell=True)
    subprocess.call('/usr/bin/pkill -9 rtl_tcp', shell=True)
    # Also found that I need to hard kill this process as well (suicide)
    subprocess.call('/usr/bin/pkill -9 meter_mobile', shell=True)
    sys.exit(0)


class MeterReader(threading.Thread):

    def __init__(self, meter_ids, reading_files=[]):

        # Call main class constructor
        threading.Thread.__init__(self)

        # save set of meter ids.
        self._meter_ids = meter_ids

        # Save the list of file paths to log the readings to
        self._reading_files = reading_files

        # start meter reading process
        self._rtlamr = subprocess.Popen([RTLAMR_PATH, 
            '-gainbyindex=24',   # index 24 was found to be the most sensitive
            '-format=csv'], stdout=subprocess.PIPE)

        # meter ids of the last 3 readings that were in the meter list
        # First one in list is the oldest 
        self.last_ids = [''] * 3    # start all blank

        # Number of total readings (including those that don't match the meter list)
        self.total_readings = 0

    def run(self):

        # listen for meter readings indefinitely
        while True:

            try:
                flds = self._rtlamr.stdout.readline().strip().split(',')

                if len(flds) != 9:
                    # valid readings have nine fields
                    continue

                self.total_readings += 1

                # If the list of Meter IDs to record is not empty, make sure this ID
                # is in the list of IDs to record.
                # Get the time, the meter ID and the reading
                ts_cur = int(time.time())
                meter_id = int(flds[3])
                read_cur = int(flds[7])

                # if meter is in the list, update the list of last IDs received
                # and log the data to the file list.
                if meter_id in self._meter_ids:
                    # add the new ID at the end, and bump the oldest one off
                    self.last_ids = self.last_ids[1:] + [meter_id]

                    # log the reading to all of the log files
                    for fn in self._reading_files:
                        with open(fn, 'a', 0) as fout:   # append to file, unbuffered
                            fout.write('%s\t%s\t%s\n' % (ts_cur, meter_id, read_cur))
                            os.fsync(fout)    # just to make sure it is written

            except:
                logging.exception('Error processing reading %s' % flds)
                time.sleep(2)


# Delay to make sure that rtltcp has found the RTL-SDR dongle.  Just
# to be cautious, break into a number delays in case time.sleep() might
# be affected by ntpd changes to system clock.
# 18 loops x 5 seconds = 90 second delay
for i in range(18):       # Set this to 18 for 90 second delay
    remaining = 90 - i*5
    display('Warming Up\n%s secs remaining' % remaining)
    time.sleep(5)

# Configure logging and log a restart of the app
config_logging.configure_logging(logging, ERROR_LOG_FILE)
logging.warning('meter_mobile has restarted')

# If process is being killed, go through shutdown process
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# Read in the list of meter IDs to store and put in set.
try:
    meter_ids = set([int(x) for x in open(METER_ID_FILE).readlines() if len(x.strip())])
except:
    display('Error: No\nMeter ID List')
    logging.exception('Error reading Meter ID List.')
    time.sleep(3)
    sys.exit(1)

# start the meter reader
reader = MeterReader(meter_ids, READING_FILES)
reader.start()

while True:
    try:
        time.sleep(2)
        ids = reader.last_ids
        msg = '%s  %s\n*%s*    %s' % (
            ids[0],
            ids[1],
            ids[2],
            reader.total_readings % 100    # last two digits
        )
        display(msg)
    except:
        logging.exception('Error processing meter readings')
