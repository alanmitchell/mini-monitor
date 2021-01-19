#!/usr/bin/env python3
"""Main script to start and control the data logger.
"""
from os.path import dirname, realpath, join, exists
import os
import sys, logging, logging.handlers, json
import shutil
import time
import subprocess
import requests
import logger_controller
import scripts.utils
import config_logging

# Configure logging and log a restart of the app
config_logging.configure_logging(logging, '/var/log/pi_log.log')
logging.warning('pi_logger has restarted')

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

# ************* KEEP THIS UPDATED AS CHANGES ARE MADE ******************
# Set the Software Version number as a property on the Settings module
#
# Version 3.3:  Added Modbus RTU Reader.
# Version 3.2:  Added Modbus TCP Reader.
# Version 3.1:  Added onewire.OneWire Reader.  Upgraded raspbian packages.
#               Added delay between starting rtl_tcp and rtlamr.
# Version 3.0:  Python 3 version.
# Version 2.3:  Added MF197 Cellular Modem in serial mode
# Version 2.2:  Added Outage Monitor reader.
# Version 2.1:  2017-11-02: Improved meter reader start up & WiFi reliability
# Version 2.0:  Added Commodity ID to Sensor ID for Meter Reader
# Version 1.9:  2017-08-28. GUI utility for editing Settings File.
# Version 1.8:  2017-08-11. Meter Reader and Cellular modem changes.
# Version 1.7:  Implmented MQTT Broker and restructured app to use it.
#               Add the Utility Meter reader script.
# Version 1.6:  Requirements file. Control over Reboot tests. Removed
#               Cell modem code, cuz using UMTSkeeper now.
# Version 1.5:  Added posting of IP Addresses in initial debug output.
# Version 1.4:  Added Sensaphone reader class.
#
settings.VERSION = 3.3
#***********************************************************************

# Create the object to control the reading and logging process
controller = logger_controller.LoggerController(read_interval=settings.READ_INTERVAL, 
                                    log_interval=settings.LOG_INTERVAL)
logging.debug('Created logging controller.')

# Add the sensor readers listed in the settings file to the controller
# and post an initial set of readings to the debug URL.
init_readings = []
for reader_name in settings.READERS:
    
    try:
        # Dynamically import the module containing the reader class
        parts = ('readers.' + reader_name).split('.')
        mod = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]])
        
        # get the reader class, instantiate it and add it to the controller, 
        # passing in settings module for use by the class.  Also, get an 
        # initial set of readings from the reader.
        klass = getattr(mod, parts[-1])
        reader_obj = klass(settings)
        controller.add_reader(reader_obj)
        try:
            init_readings += reader_obj.read()
            logging.debug('Created and initially read %s' % reader_name)
        except:
            logging.exception('Error getting initial readings from %s reader' % reader_name)
        
    except:
        logging.exception('Error starting %s reader' % reader_name)

# wait for up to one minute for the network to be available
for i in range(30):
    try:
        subprocess.check_call(['/usr/bin/curl', 'http://google.com'])
        logging.debug('Network is available')
        break
    except:
        # if curl returns non-zero error code, an exception is raised
        # wait and try again
        time.sleep(2)

# post the initial readings to the Debug URL
try:
    # first, add the IP addresses assigned to this system to the readings
    init_readings += scripts.utils.ip_addrs()
    init_readings.append('Logger ID: %s' % settings.LOGGER_ID)
    requests.post('http://api.analysisnorth.com/debug_store', data=json.dumps(init_readings), headers={'content-type': 'application/json'})
    logging.debug('Successfully posted First Readings.')
except:
    logging.exception('Error posting initial readings to Debug URL.')

# If there are any readers active then run the controller.  Otherwise exit.
if len(controller.readers):
    try:
        # start the reading/logging
        controller.run()
    except:
        logging.exception('Error occurred in the run() method of the logging controller.')
