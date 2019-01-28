#!/usr/bin/python
"""Run by cron every 15 minutes.  Does numerous health checks, applying 
remedies and rebooting if needed.
"""
import subprocess
import time
import sys
import calendar
import os
import cron_logging
import utils

# get the logger for the application
logger = cron_logging.logger

try:
    # parse seconds of uptime out of proc file.
    uptime = float( open('/proc/uptime').read().split()[0] )
except:
    logger.exception('Error determining uptime. Rebooting.')
    utils.reboot()

# don't do these tests if the system has not been up for 15 minutes
# sys.exit() throws an exception so need to do this outside the above try
# block.
if uptime < 15 * 60:
    sys.exit()

# the wall clock minute that this script is being run
cur_min = time.localtime().tm_min

# only run these tasks once per hour (at the 30 minute time point)
if cur_min > 20 and cur_min < 40:

    # backup log and Post database files to non-volatile storage
    utils.backup_files()

