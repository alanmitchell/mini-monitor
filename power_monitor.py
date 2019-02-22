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
from loglib import change_detect

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
    instr.serial.timeout = 0.2
    instr.serial.baudrate = 9600

except:
    logging.exception('Error initializing the script.')
    sys.exit(1)

# Arrays to hold the timestamps and readings for the values of importance
# from the sensor
tstamps = []
powers = []
volts = []
amps = []
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
        amps.append((data[1] + data[2]*65536) * 0.001 / settings.PWR_CT_WRAPS)
        powers.append((data[3] + data[4]*65536) * 0.1 / settings.PWR_CT_WRAPS)
        freqs.append(data[7]*0.1)
        pfs.append(data[8]*0.01)

    # see if it is time to post summarized readings
    if time.time() > next_log_time:
        # Deal with clock catch-up when the Pi has been off.
        next_log_time = max(next_log_time + settings.LOG_INTERVAL, time.time() + settings.LOG_INTERVAL - 2.0)
        

        # If there is any data, process into desired form and post it
        if len(tstamps):

            try:
                # Convert arrays into numpy arrays
                tstamps = np.array(tstamps)
                volts = np.array(volts)
                amps = np.array(amps)
                powers = np.array(powers)
                freqs = np.array(freqs)
                pfs = np.array(pfs)

                # gathers lines to post to MQTT
                lines_to_post = []

                # first include the average power if requested
                if settings.PWR_INCL_PWR_AVG:
                    ts_avg = tstamps.mean()
                    pwr_avg = powers.mean()
                    lines_to_post.append('%s\t%s\t%s' % (ts_avg, logger_id + '_pwr_avg', pwr_avg))

                # Now add detail points for each of the requested measurements
                measures = [
                    ('pwr', powers),
                    ('volt', volts),
                    ('amp', amps),
                    ('freq', freqs),
                    ('pf', pfs)
                ]
                for lbl, val_array in measures:
                    if getattr(settings, 'PWR_INCL_' + lbl.upper()):
                        lines_to_post += change_detect.make_post_lines(
                            '%s_%s' % (logger_id, lbl),
                            tstamps,
                            val_array,
                            getattr(settings, 'PWR_THRESHOLD_' + lbl.upper()),
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

            tstamps = []
            powers = []
            volts = []
            amps = []
            freqs = []
            pfs = []
            
