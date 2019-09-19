#!/usr/bin/env python3
"""Script to read and post to BMON Acurite 592TXR Temperature/Humidity Wireless sensors,
which operate in the 433 MHz band.
"""

import subprocess
import time
import calendar
import signal
import sys
import logging
import threading
import queue
import numpy as np
import mqtt_poster
import config_logging


class RTLreceiver(threading.Thread):
    """Class that runs in a separate thread and receives sensor readings
    through the RTL-SDR radio.  Each reading is one line and is stored
    in a FIFO Queue for retrieval by the main thread.
    """

    def __init__(self):
        threading.Thread.__init__(self)

        # If only thing left running are daemon threads, Python will exit.
        self.daemon = True
        self._rtl433 = subprocess.Popen(
            ['/usr/local/bin/rtl_433', '-R40', '-Fjson', '-U'], 
            stdout=subprocess.PIPE,
            text=True)
        self._lines = queue.Queue()
        self._stop_thread = False

    def run(self):
        while True:
            lin = self._rtl433.stdout.readline().strip()
            self._lines.put(lin)
            if self._stop_thread:
                break

    def readings_available(self):
        """Returns True if there are readings available in the Queue.
        """
        return (self._lines.qsize() > 0)

    def get_reading(self):
        """Returns a reading line from the Queue.
        """
        a_line = self._lines.get()
        self._lines.task_done()
        return a_line

    def kill(self):
        """Kills the RTL-433 receiver software and stops this thread.
        """
        self._stop_thread = True
        self._rtl433.kill()


def shutdown(signum, frame):
    '''Kills the RTL 433 receiver thread that was started by this script.
    '''
    rtl_receiver.kill()
    sys.exit(0)

# create a dictionary to hold all the readings collected during a
# logging interval.  The keys of the dictionary will be the reading ID,
# the values will be a list of readings, each reading being a tuple of the form:
# (timestamp, value)
final_read_data = {}

def add_readings(ts, id, values):
    """Adds a temperature and RH reading to the final reading dictionary.
    'ts' is a Unix timestamp (seconds past the Epoch)
    'id' is the ID number transmitted by the sensor.
    'values' is a two-tuple: (temperature reading deg F, RH in %)
    ** Really need to put the storage and summarization of readings in a
    separate class, reusable by other scripts like this.
    """
    val_temp, val_rh = values   # split into temp and RH readings

    # Add temperature reading
    final_id = '%s_%s_temp' % (logger_id, id)
    read_list = final_read_data.get(final_id, [])
    read_list.append( (ts, val_temp))
    final_read_data[final_id] = read_list

    # Add RH reading
    final_id = '%s_%s_rh' % (logger_id, id)
    read_list = final_read_data.get(final_id, [])
    read_list.append( (ts, val_rh))
    final_read_data[final_id] = read_list

# Main Script body here
if __name__=="__main__":

    try:

        # Configure logging and log a restart of the app
        config_logging.configure_logging(logging, '/var/log/rtl433_reader.log')
        logging.warning('rtl433_reader has restarted')

        # The settings file is installed in the FAT boot partition of the Pi SD card,
        # so that it can be easily configured from the PC that creates the SD card.
        # Include that directory in the Path so the settings file can be found.
        sys.path.insert(0, '/boot/pi_logger')
        import settings

        # Start the RTL_433 receiver
        rtl_receiver = RTLreceiver()
        rtl_receiver.start()

        # If process is being killed, go through shutdown process
        signal.signal(signal.SIGTERM, shutdown)
        signal.signal(signal.SIGINT, shutdown)

        # Start up the object that will post the final readings to the MQTT
        # broker.
        mqtt = mqtt_poster.MQTTposter()
        mqtt.start()

        # determine the time when the next summarized post will occur
        next_log_time = time.time() + settings.LOG_INTERVAL

        # get the base Logger ID from the settings file
        logger_id = settings.LOGGER_ID

    except:
        logging.exception('Error initializing the script.')
        sys.exit(1)

    # These hold the raw readings coming from the RTL-SDR receiver.  The keys
    # are a two-tuple (date/time string, id).  The values are a list of two-tuples
    # (temperature in deg F, humidity in %).
    # These readings are transmitted three times in a row from the sensor.
    # The code below adds all the received transmissions to the 'readings' dictionary
    # and then considers them valid if there are at least two transmissions that match.
    readings = {}

    while True:
        time.sleep(1)
        try:
            lin = ''    # in case we error before a line is read.
            while rtl_receiver.readings_available():
                lin = rtl_receiver.get_reading()
                flds = eval(lin)
                k = (flds['time'], flds['id'])
                val_list = readings.get(k, [])
                val_list.append( (flds['temperature_C'] * 1.8 + 32.0, flds['humidity']) )
                readings[k] = val_list

        except:
            logging.exception('Error processing a sensor reading: %s' % lin)

        # process any items in the reading list that have 3 values or are older than 4 seconds ago
        for ky, vals in list(readings.items()):
            try:
                ts_str, id = ky
                ts = time.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                ts = calendar.timegm(ts)
                if len(vals) == 3 or (time.time() - ts >= 4.0):
                    del readings[ky]

                    # only process if there are at least two readings
                    if len(vals) >= 2:
                        # sort the readings
                        vals = sorted(vals)
                        # try to find two matching readings
                        if vals[0] == vals[1]:
                            add_readings(ts, id, vals[0])
                        elif vals[-1] == vals[-2]:
                            add_readings(ts, id, vals[-1])
            except:
                logging.exception('Error processing %s: %s' % (ky, vals))

        # see if it is time to post summarized readings
        if time.time() > next_log_time:
            # Deal with clock catch-up when the Pi has been off.
            next_log_time = max(next_log_time + settings.LOG_INTERVAL, time.time() + settings.LOG_INTERVAL - 2.0)

            lines_to_post = []
            for reading_id, reading_list in list(final_read_data.items()):
                try:
                    # make a separate numpy array of values and time stamps
                    rd_arr = np.array(reading_list)
                    ts_arr = rd_arr[:, 0]  # first column
                    val_arr = rd_arr[:, 1]  # second column
                    # calculate the average value to log
                    val_avg = val_arr.mean()
                    # limit this value to 5 significant figures
                    val_avg = float('%.5g' % val_avg)
                    # calculate the average timestamp to log and convert to
                    # integer seconds
                    ts_avg = int(ts_arr.mean())
                    lines_to_post.append(
                        '%s\t%s\t%s' % (ts_avg, reading_id, val_avg)

                    )
                except:
                    logging.exception('Error preparing to post: %s' % reading_id)

            # clear out readings to prep for next logging period
            final_read_data = {}

            # Post the summarized readings
            try:
                if len(lines_to_post):
                    mqtt.publish(
                        'readings/final/rtl433_reader',
                        '\n'.join(lines_to_post)
                    )
                    logging.info('%d readings posted.' % len(lines_to_post))
            except:
                logging.exception('Error posting: %s' % lines_to_post)
