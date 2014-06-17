#!/usr/bin/python
"""This script uploads the two pi_logger error/debug log files to the 
analysisnorth.com server.
"""

import datetime, sys
import requests

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
    files = {'upfile': ('%s_pi_cron.log' % prefix, open('/boot/pi_logger/logs/pi_cron.log', 'rb'))}
    r = requests.post(url, files=files, data=data)

except:
    print 'Error uploading log files'