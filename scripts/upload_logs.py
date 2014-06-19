#!/usr/bin/python
"""This script uploads the two pi_logger error/debug log files to the 
analysisnorth.com server.  Also uploads the tails of some system log files.
"""

import datetime, sys, subprocess, logging
import requests
import cron_logging

# This script is execute in rc.local and must not error out or it will stop
# execution of rc.local (although I've double protected by using the command
# "set +e" in the rc.local script).
try:

    # The settings file is installed in the FAT boot partition of the Pi SD card,
    # so that it can be easily configured from the PC that creates the SD card.  
    # Include that directory in the Path so the settings file can be found.
    sys.path.insert(0, '/boot/pi_logger')
    import settings
    
    # get the system ID for this logger
    sys_id = settings.LOGGER_ID
    
    # Make a datetime string
    ts = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
    
    prefix = '%s_%s' % (sys_id, ts)
    
    url = 'http://analysisnorth.com/marie/upload.php'
    files = {'upfile': ('%s_pi_log.log' % prefix, open('/boot/pi_logger/logs/pi_log.log', 'rb'))}
    data = {'MAX_FILE_SIZE': '500000'}
    r = requests.post(url, files=files, data=data)
    
    # read the cron_log file. this ensures it is closed in case an error occurs
    # and the logging statement in the error handler needs access to the file.
    log_contents = open('/boot/pi_logger/logs/pi_cron.log').read()
    files = {'upfile': ('%s_pi_cron.log' % prefix, log_contents)}
    r = requests.post(url, files=files, data=data)
    
    # get tails of important system log files
    tail_syslog = subprocess.check_output('/usr/bin/tail -n500 /var/log/syslog', shell=True)
    tail_daemon = subprocess.check_output('/usr/bin/tail -n200 /var/log/daemon.log', shell=True)
    report = 'Last 500 lines of syslog:\n\n%s\n\nLast 200 lines of daemon.log:\n\n%s' % (tail_syslog, tail_daemon)
    files = {'upfile': ('%s_system.log' % prefix, report)}
    r = requests.post(url, files=files, data=data)

except:
    logging.exception('Error uploading log files.')