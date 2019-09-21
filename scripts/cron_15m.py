#!/usr/bin/env python3
"""Run by cron every 15 minutes.  Does numerous health checks, applying 
remedies and rebooting if needed.
"""
import subprocess
import time
import sys
import calendar
import os

sys.path.insert(0, '../')

import scripts.cron_logging
from scripts.utils import reboot, backup_files

# get the logger for the application
logger = scripts.cron_logging.logger

try:
    # parse seconds of uptime out of proc file.
    uptime = float( open('/proc/uptime').read().split()[0] )
except:
    logger.exception('Error determining uptime. Rebooting.')
    reboot()

# don't do these tests if the system has not been up for 20 minutes
# sys.exit() throws an exception so need to do this outside the above try
# block.
if uptime < 20 * 60:
    sys.exit()

try:
    # the wall clock minute that this script is being run
    cur_min = time.localtime().tm_min

    # import the settings file
    sys.path.insert(0, '/boot/pi_logger')
    import settings

    # If the meter reader is running and there hasn't been a gas reading
    # in the last 15 minutes, reboot.
    if settings.ENABLE_METER_READER:
        # the file that holds the last gas reading
        gas_file = '/var/run/last_gas'
        if not os.path.exists(gas_file):
            # No gas reading at all has occurred
            reboot()
        else:
            # Get the time the file was last modified, indicating the 
            # last valid reading.  If not modified in the last
            # 15 minutes, reboot.
            if time.time() - os.path.getmtime(gas_file) > 15 * 60:
                reboot()

    # if the system has been up for more than settings.REBOOT_DAYS, force
    # a reboot.  Never reboot if REBOOT_DAYS=0.
    if settings.REBOOT_DAYS>0 and uptime > settings.REBOOT_DAYS * 3600 * 24:
        logger.info('Reboot due to %s days of uptime.' % settings.REBOOT_DAYS)
        reboot()

    # if WiFi is being used (as evidenced by an SSID in the wpa_supplicant file)
    # try to ping Google and if no response, cycle the WiFi interface.
    if 'ssid' in open('/etc/wpa_supplicant/wpa_supplicant.conf').read():
        subprocess.call(
            '/bin/ping -q -c2 8.8.8.8 || (/sbin/ifdown --force wlan0;/sbin/ifup wlan0)',
            shell=True
        )

    # Count the number of logged errors that occurred in the last 5 minutes and
    # reboot if an excessive count.
    # Log file timestamps are in UTC.
    fname = '/var/log/pi_log.log'
    if settings.CHECK_ERROR_CT and os.path.exists(fname):
        error_ct = 0
        now = time.time()
        for lin in open(fname):
            # ignore posting errors, which are caused by no network. That is dealt
            # with separately.
            if ('- ERROR -' in lin) and ('Error posting' not in lin):
                parts = lin.split(',')
                err_tm = calendar.timegm(time.strptime(parts[0], '%Y-%m-%d %H:%M:%S'))
                if now - err_tm < 300:
                    error_ct += 1
        if error_ct > 50:
            logger.error('Rebooting due to %s errors during last 5 minutes.' % error_ct)
            reboot()
except:
    logger.exception('Error performing health checks. Rebooting.')
    reboot()

# Check to see if last successful post was too long ago
# If so, reboot.
try:
    if settings.CHECK_LAST_POST:
        # If the Settings file has the LAST_POST_REBOOT_DELAY setting
        # use it to determine how long of wait needs to occur before
        # rebooting.
        if hasattr(settings, 'LAST_POST_REBOOT_DELAY'):
            post_max = settings.LAST_POST_REBOOT_DELAY * 3600  # convert to seconds
        else:
            # No LAST_POST_REBOOT_DELAY setting in the Settings file.  So,
            # use this formula for the delay:
            # trigger reboot if no post in last hour or 1.2 x post interval,
            # whichever is greater.
            post_max = max(3600, 1.2 * settings.LOG_INTERVAL)

        # but don't do the test if the system has not been up that long
        if uptime > post_max:
            last_post_time = float(open('/var/run/last_post_time').read())
            if (time.time() - last_post_time) > post_max:
                logger.error('Rebooting due to last successful post being too long ago.')
                reboot()
except:
    # could get an error from missing last_post_time file, but it should be
    # there as we don't execute this test until enough time has passed for a
    # post to occur.
    logger.exception('Error checking last post time. Rebooting.')
    reboot()

# only run these tasks once per hour (at the 30 minute time point)
if cur_min > 20 and cur_min < 40:

    # backup log and Post database files to non-volatile storage
    backup_files()

