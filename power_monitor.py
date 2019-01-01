#!/usr/bin/env python
"""Script to read a PZEM-016 Electric Power sensor.  Readings are posted
to the readings/final/power_monitor MQTT topic.

Uses a number of settings from the Mini-Monitor settings file.  See
system_files/settings_template.py, "Power Monitor" section for those 
settings.
"""

import time
import sys
import logging
import numpy as np
import minimalmodbus
import mqtt_poster
import config_logging
from tools import utils

def make_post_lines(sensor_id, time_stamps, values, change_threshold, max_interval):
    """Returns an array of lines to post to the MQTT broker.  Only posts changes in 
    values.
    'sensor_id': sensor ID to use for each line
    'time_stamps': numpy array of time stamps associated with the values
    'values': numpy array of values to scan for changes and post accordingly
    'change_threshold': amount of change that needs to occur before inclusion
    'max_interval': maximum number of points to separate posts.  Will post w/o a change to meet this.
    """
    # find the indexes to include in the post lines
    ixs = utils.find_changes(values, change_threshold, max_interval=max_interval)
    ts_incl = time_stamps[ixs]
    val_incl = values[ixs]
    return ['%s\t%s\t%s' % (ts, sensor_id, val) for ts, val in zip(ts_incl, val_incl)]

# Main Script body here
if __name__=="__main__":

    try:

        # Configure logging and log a restart of the app
        config_logging.configure_logging(logging, '/var/log/power_monitor.log')
        logging.warning('power_monitor has restarted')

        # The settings file is installed in the FAT boot partition of the Pi SD card,
        # so that it can be easily configured from the PC that creates the SD card.
        # Include that directory in the Path so the settings file can be found.
        sys.path.insert(0, '/boot/pi_logger')
        import settings

        # Start up the object that will post the final readings to the MQTT
        # broker.
        mqtt = mqtt_poster.MQTTposter()
        mqtt.start()

        # determine the time when the next summarized post will occur
        next_log_time = time.time() + settings.LOG_INTERVAL

        # get the base Logger ID from the settings file
        logger_id = settings.LOGGER_ID

        # Set up the MODBUS instrument used to read the sensor
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        instr = minimalmodbus.Instrument(settings.PWR_PORT, 1)   # Slave Address 1 assumed for sensor
        instr.serial.timeout = 0.1
        instr.serial.baudrate = 9600

    except:
        logging.exception('Error initializing the script.')
        sys.exit(1)

    # Arrays to hold the timestamps and readings for the values of importance
    # from the sensor
    tstamps = []
    powers = []
    volts = []
    freqs = []
    pfs = []

    while True:
        time.sleep(0.91)

        ts = time.time()
        data = None
        for i in range(5):
            try:
                data = instr.read_registers(0, 10, 4)
                break
            except:
                logging.exception('Error reading PZEM-016.')
        if data:
            tstamps.append(ts)
            volts.append(data[0]*0.1)
            powers.append((data[3] + data[4]*65536) * 0.1 / settings.PWR_CT_WRAPS)
            freqs.append(data[7]*0.1)
            pfs.append(data[8]*0.01)

        # see if it is time to post summarized readings
        if time.time() > next_log_time:
            next_log_time += settings.LOG_INTERVAL

            # If there is any data, process into desired form and post it
            if len(tstamps):

                try:
                    # Convert arrays into numpy arrays
                    tstamps = np.array(tstamps)
                    volts = np.array(volts)
                    powers = np.array(powers)
                    freqs = np.array(freqs)
                    pfs = np.array(pfs)

                    # first include the average power
                    ts_avg = tstamps.mean()
                    pwr_avg = powers.mean()
                    lines_to_post = ['%s\t%s\t%s' % (ts_avg, logger_id + '_pwr_avg', pwr_avg)]

                    # Now add detail points for each of the measurements
                    lines_to_post += make_post_lines(
                        logger_id + '_pwr',
                        tstamps,
                        powers,
                        settings.PWR_THRESHOLD_PWR,
                        settings.PWR_MAX_INTERVAL
                    )
                    lines_to_post += make_post_lines(
                        logger_id + '_volt',
                        tstamps,
                        volts,
                        settings.PWR_THRESHOLD_VOLT,
                        settings.PWR_MAX_INTERVAL
                    )
                    lines_to_post += make_post_lines(
                        logger_id + '_freq',
                        tstamps,
                        freqs,
                        settings.PWR_THRESHOLD_FREQ,
                        settings.PWR_MAX_INTERVAL
                    )
                    lines_to_post += make_post_lines(
                        logger_id + '_pf',
                        tstamps,
                        pfs,
                        settings.PWR_THRESHOLD_PF,
                        settings.PWR_MAX_INTERVAL
                    )

                except:
                    logging.exception('Error summarizing readings.')

                # Post the summarized readings
                try:
                    if len(lines_to_post):
                        mqtt.publish(
                            'readings/final/power_monitor',
                            '\n'.join(lines_to_post)
                        )
                        logging.info('%d readings posted.' % len(lines_to_post))
                except:
                    logging.exception('Error posting: %s' % lines_to_post)
