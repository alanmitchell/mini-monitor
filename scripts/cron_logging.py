"""Sets up logging for the various cron scripts.
"""
import logging, logging.handlers, sys

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

# Log file for the application.  Need to be root to write to this directory.
# So, must start this app as root.
LOG_FILE = '/var/log/pi_cron.log'

# Use the 'pi_cron' logger for the application.
logger = logging.getLogger('pi_cron')

# set the log level. Because we are setting this on the logger, it will apply
# to all handlers (unless maybe you set a specific level on a handler?).
logger.setLevel(settings.LOG_LEVEL)

# create a rotating file handler
fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=200000, backupCount=5)

# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
fh.setFormatter(formatter)

# create a handler that will print to console as well.
console_h = logging.StreamHandler()
console_h.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(console_h)


