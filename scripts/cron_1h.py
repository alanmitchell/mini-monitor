#!/usr/bin/python
"""Runs via cron every hour.
Checks for error conditions and reboots the system if any are detected.
Assumes that this script is run as the root user.
"""
import time, subprocess, calendar, datetime, logging
import cron_logging, utils

    
# only run these tasks every one hour
if datetime.datetime.now().hour % 1 == 0:
    
    # record the total number of bytes passed through the ppp0 interface
    try:
        res = subprocess.check_output('/sbin/ifconfig | grep -A7 ppp0 | grep "RX bytes"', shell=True)
        parts = res.split(':')
        rx_bytes = int(parts[1].split()[0])
        tx_bytes = int(parts[2].split()[0])
        logging.info('Cellular Byte Total: %d' % (rx_bytes + tx_bytes))
    except:
        pass
            
    # Check to see if last successful post was more than 1 hour ago.
    # If so, reboot.
    try:
        last_post_time = float(open('/home/pi/pi_logger/last_post_time').read())
        if (time.time() - last_post_time) > 60 * 60.0:
            logging.error('Rebooting due to last successful post being more than 1 hour ago.')
            utils.reboot()
    except:
        pass
    
    # Count the number of logged errors that occurred in the last hour and reboot
    # if an excessive count.
    # Log file timestamps are in UTC.
    try:
        fname = '/boot/pi_logger/logs/pi_log.log'
        error_ct = 0
        now = time.time()
        for lin in open(fname):
            if 'ERROR' in lin:
                parts = lin.split(',')
                err_tm = calendar.timegm(time.strptime(parts[0], '%Y-%m-%d %H:%M:%S'))
                if now - err_tm < 3600:
                    error_ct += 1
        if error_ct > 75:
            logging.error('Rebooting due to %s errors during last hour.' % error_ct)
            utils.reboot()
    except:
        pass
