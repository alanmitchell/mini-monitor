#!/usr/bin/python
"""Run by cron every 15 minutes.  Does numerous health checks, applying 
remedies and rebooting if needed.
"""
import subprocess, time, logging, sys, calendar, os, glob
import cron_logging, utils

try:
    # parse seconds of uptime out of proc file.
    uptime = float( open('/proc/uptime').read().split()[0] )
except:
    logging.exception('Error determining uptime. Rebooting.')
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
    if settings.REBOOT_DAYS>0 and uptime > REBOOT_DAYS * 3600 * 24:
        logging.info('Reboot due to %s days of uptime.' % settings.REBOOT_DAYS)
        utils.reboot()
    
    # if the one wire system is being used, check to see if the USB adapter ID
    # chip is present in OWFS.  If not, there is a OWFS problem. OWFS malfunction
    # will generally not trigger read error, as no sensors will be found and no
    # readings will occur.
    if 'onewire.OneWireReader' in settings.READERS:
        ok = False
        # try two times to find ID chip
        for i in range(2):
            f_list = glob.glob('/mnt/1wire/uncached/81.*')  # 81 is family code of ID chip.
            if len(f_list)>0:
                ok = True
                break
        if not ok:
            logging.error('OWFS system is not working. Rebooting.')
            utils.reboot()
    
    # Count the number of logged errors that occurred in the last 5 minutes and 
    # reboot if an excessive count.
    # Log file timestamps are in UTC.
    fname = '/boot/pi_logger/logs/pi_log.log'
    if os.path.exists(fname):
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
        if error_ct > 6:
            logging.error('Rebooting due to %s errors during last 5 minutes.' % error_ct)
            utils.reboot()
except:
    logging.exception('Error performing health checks. Rebooting.')
    utils.reboot()

# only run these tasks once per hour (in first 15 minute interval)
if cur_min < 15:
    
    # record the total number of bytes passed through the ppp0 interface
    try:
        res = subprocess.check_output('/sbin/ifconfig | /bin/grep -A7 ppp0 | /bin/grep "RX bytes"', shell=True)
        parts = res.split(':')
        rx_bytes = int(parts[1].split()[0])
        tx_bytes = int(parts[2].split()[0])
        logging.info('Cellular Byte Total: %d' % (rx_bytes + tx_bytes))
    except:
        # not critical, don't reboot
        pass
            
    # Check to see if last successful post was too long ago
    # If so, reboot.
    try:
        # trigger reboot if no post in last hour or 1.2 x post interval, 
        # whichever is greater.
        post_max = max(3600, 1.2 * settings.LOG_INTERVAL)
        
        # but don't do the test if the system has not been up that long
        if uptime > post_max:
            last_post_time = float(open('/home/pi/pi_logger/last_post_time').read())
            if (time.time() - last_post_time) > post_max:
                logging.error('Rebooting due to last successful post being too long ago.')
                utils.reboot()
    except:
        # could get an error from missing last_post_time file, but it should be
        # there as we don't execute this test until enough time has passed for a
        # post to occur.
        logging.exception('Error checking last post time. Rebooting.')
        utils.reboot()

# check to see if the network is working.  If not, kill wvdial and restart it.
# I put it at the end to ensure critical errors were caught above before this.
try:
    subprocess.check_output(['/usr/bin/nslookup', 'gci.net'])
except:
    # if nslookup returns non-zero error code, an exception is raised
    logging.error('No network connection. Restarting cellular modem.')
    subprocess.call('/home/pi/pi_logger/scripts/start_cell_internet.py', shell=True)
    