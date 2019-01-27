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
import time
import logging
import json
import requests
import mqtt_poster
import config_logging

def display(text):
    """Displays 'text' on the USB connected display; lines are delimited
    by newline characters.  The display is first cleared before displaying
    the new message.
    """
    print(text)

# Delay to make sure that rtltcp has found the RTL-SDR dongle.  Just
# to be cautious, break into a number delays in case time.sleep() might
# be affected by ntpd changes to system clock.
# 18 loops x 5 seconds = 90 second delay
for i in range(18):
    remaining = 90 - i*5
    display('Warming Up\n{remaining} secs remaining')
    time.sleep(5)
display('Waiting for\nFirst Reading')
# Configure logging and log a restart of the app
config_logging.configure_logging(logging, '/var/log/meter_mobile.log')
logging.warning('meter_mobile has restarted')

def shutdown(signum, frame):
    '''Kills the external processes that were started by this script
    '''
    # Hard kill these processes and I have found them difficult to kill with SIGTERM
    subprocess.call('/usr/bin/pkill -9 rtlamr', shell=True)
    subprocess.call('/usr/bin/pkill -9 rtl_tcp', shell=True)
    # Also found that I need to hard kill this process as well (suicide)
    subprocess.call('/usr/bin/pkill -9 meter_mobile', shell=True)
    sys.exit(0)

# If process is being killed, go through shutdown process
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# Read in the list of meter IDs to store and put in set.
try:
    meter_ids = set([int(x) for x in open('/boot/meters.txt').readlines() if len(x.strip())])
except:
    display('Error: No\nMeter ID List')
    logging.exception('Error reading Meter ID List.')
    time.sleep(3)
    sys.exit(1)

# start the rtlamr program.
rtlamr = subprocess.Popen(['/home/pi/gocode/bin/rtlamr', 
    '-gainbyindex=24',   # index 24 was found to be the most sensitive
    '-format=csv'], stdout=subprocess.PIPE)

while True:

    try:
        flds = rtlamr.stdout.readline().strip().split(',')

        if len(flds) != 9:
            # valid readings have nine fields
            continue

        # If the list of Meter IDs to record is not empty, make sure this ID
        # is in the list of IDs to record.
        meter_id = int(flds[3])

        ts_cur = time.time()
        read_cur = int(flds[7])
        

    except:
        logging.exception('Error processing reading %s' % flds)
        time.sleep(2)
