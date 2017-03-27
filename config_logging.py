"""Module used to configure exception logging in a consistent way across 
all the scripts used by the mini-monitor system.
"""

import logging.handlers
import sys

# Access the mini-monitor settings file
# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

def configure_logging(logging_module, log_file_path):
    """Configures the logging for an application.  Use this by:
           import logging
           import config_logging
           config_logging.configure_logging(logging, '/var/log/logfilename')
    """

    # Use the root logger for the application.

    # set the log level. Because we are setting this on the logger, it will apply
    # to all handlers (unless maybe you set a specific level on a handler?).
    logging_module.root.setLevel(settings.LOG_LEVEL)

    # Set logging level and stop propagation of messages from the 'requests' module
    logging_module.getLogger('requests').propagate = False
    logging_module.getLogger("requests").setLevel(logging_module.WARNING)
    logging_module.getLogger("urllib3").setLevel(logging_module.WARNING)

    # create a rotating file handler
    fh = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=200000, backupCount=5)

    # create formatter and add it to the handler
    formatter = logging_module.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    fh.setFormatter(formatter)

    # create a handler that will print to console as well.
    console_h = logging_module.StreamHandler()
    console_h.setFormatter(formatter)

    # add the handlers to the root logger
    logging_module.root.addHandler(fh)
    logging_module.root.addHandler(console_h)
