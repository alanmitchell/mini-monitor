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

    # if the system has been up for more than settings.REBOOT_DAYS, force
    # a reboot.  Never reboot if REBOOT_DAYS=0.
    if settings.REBOOT_DAYS>0 and uptime > settings.REBOOT_DAYS * 3600 * 24:
        logger.info('Reboot due to %s days of uptime.' % settings.REBOOT_DAYS)
        utils.reboot()
    
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
            utils.reboot()
except:
    logger.exception('Error performing health checks. Rebooting.')
    utils.reboot()

# only run these tasks once per hour (at the 30 minute time point)
if cur_min > 20 and cur_min < 40:

    # backup log and Post database files to non-volatile storage
    utils.backup_files()

    # record the total number of bytes passed through the ppp0 interface
    try:
        res = subprocess.check_output('/sbin/ifconfig | /bin/grep -A7 ppp0 | /bin/grep "RX bytes"', shell=True)
        parts = res.split(':')
        rx_bytes = int(parts[1].split()[0])
        tx_bytes = int(parts[2].split()[0])
        logger.info('Cellular Byte Total: %d' % (rx_bytes + tx_bytes))
    except:
        # not critical, don't reboot.  Will also arrive here if cellular
        # modem is not being used.
        pass
            
    # Check to see if last successful post was too long ago
    # If so, reboot.
    try:
        if settings.CHECK_LAST_POST:
            # trigger reboot if no post in last hour or 1.2 x post interval,
            # whichever is greater.
            post_max = max(3600, 1.2 * settings.LOG_INTERVAL)

            # but don't do the test if the system has not been up that long
            if uptime > post_max:
                last_post_time = float(open('/var/run/last_post_time').read())
                if (time.time() - last_post_time) > post_max:
                    logger.error('Rebooting due to last successful post being too long ago.')
                    utils.reboot()
    except:
        # could get an error from missing last_post_time file, but it should be
        # there as we don't execute this test until enough time has passed for a
        # post to occur.
        logger.exception('Error checking last post time. Rebooting.')
        utils.reboot()

# If there is a cell modem present, check to see if the network is working.  
# If network not working, redial cell modem.
# I put it at the end to ensure critical errors were caught above before this.
# The /var/run/network/cell_modem contents are set in the rc.local script.
if settings.CHECK_CELL_MODEM and open('/var/run/network/cell_modem').read(1)=='1':
    try:
        subprocess.check_call(['/usr/bin/curl', 'http://google.com'])
    except:
        # if curl returns non-zero error code, an exception is raised
        logger.error('No network connection. Restarting cellular modem, if present.')
        subprocess.call('/home/pi/pi_logger/scripts/start_cell_internet.py', shell=True)
