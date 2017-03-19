#!/usr/bin/python
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

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

# ************* KEEP THIS UPDATED AS CHANGES ARE MADE ******************
# Set the Software Version number as a property on the Settings module
#
# Version 1.6:  Requirements file. Control over Reboot tests. Removed
#               Cell modem code, cuz using UMTSkeeper now.
# Version 1.5:  Added posting of IP Addresses in initial debug output.
# Version 1.4:  Added Sensaphone reader class.
#
settings.VERSION = 1.6
#***********************************************************************

# ----- Setup Exception/Debug Logging for the Application
# Log file for the application.  
LOG_FILE = '/var/log/pi_log.log'

# Use the root logger for the application.

# set the log level. Because we are setting this on the logger, it will apply
# to all handlers (unless maybe you set a specific level on a handler?).
logging.root.setLevel(settings.LOG_LEVEL)

# stop propagation of messages from the 'requests' module
logging.getLogger('requests').propagate = False

# create a rotating file handler
fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=200000, backupCount=5)

# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
fh.setFormatter(formatter)

# create a handler that will print to console as well.
console_h = logging.StreamHandler()
console_h.setFormatter(formatter)

# add the handlers to the logger
logging.root.addHandler(fh)
logging.root.addHandler(console_h)

# -------------------

# log a restart of the app
logging.warning('pi_logger has restarted')

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
    requests.post('http://api.analysisnorth.com/debug_store', data=json.dumps(init_readings), headers={'content-type': 'application/json'})
    logging.debug('Successfully posted First Readings.')
except:
    logging.exception('Error posting initial readings to Debug URL.')

try:
    # start the reading/logging
    controller.run()
except:
    logging.exception('Error occurred in the run() method of the logging controller.')

