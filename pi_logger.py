#!/usr/bin/python
"""Main script to start and control the data logger.
"""
from os.path import dirname, realpath, join
import sys, logging, logging.handlers
import httpPoster2, logger_controller

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

# The full directory path to this script file
APP_PATH = realpath(dirname(__file__))

# ----- Setup Exception/Debug Logging for the Application
# Log file for the application.  Need to be root to write to this directory.
# So, must start this app as root.
LOG_FILE = '/boot/pi_logger/logs/pi_log.log'

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

# Create the object that will post the readings to the HTTP server.
# In case of corruption of the database file that stores the readings
# to post, try sequential file names until one works.
for i in range(100):
    try:
        fname = join(APP_PATH, 'postQ%02d.sqlite' % i)
        poster = httpPoster2.HttpPoster(settings.POST_URL, 
                                        reading_converter=httpPoster2.BMSreadConverter(settings.POST_STORE_KEY),
                                        post_q_filename=join(APP_PATH, fname),
                                        post_time_file=join(APP_PATH, 'last_post_time'))
        logging.info('Post Queue file is: %s' % fname)
        break
    except:
        logging.exception('Error starting HttpPoster with queue filename: %s' % fname)

# Create the object to control the reading and logging process
controller = logger_controller.LoggerController(read_interval=settings.READ_INTERVAL, 
                                    log_interval=settings.LOG_INTERVAL)
controller.add_logging_handler(poster)   # add the HTTP poster to handle logging events

# Add the sensor readers listed in the settings file to the controller
for reader_name in settings.READERS:
    
    try:
        # Dynamically import the module containing the reader class
        parts = ('readers.' + reader_name).split('.')
        mod = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]])
        
        # get the reader class, instantiate it and add it to the controller, 
        # passing in settings module for use by the class.
        klass = getattr(mod, parts[-1])
        controller.add_reader(klass(settings))    
        
    except:
        logging.exception('Error starting %s reader' % reader_name)

try:
    # start the reading/logging
    controller.run()
except:
    logging.exception('Error occurred in the run() method of the logging controller.')
