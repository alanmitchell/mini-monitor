import subprocess
import logging
import time
import os
import shutil
import sqlite3
import cron_logging

# get the logger for the application
logger = cron_logging.logger

def reboot():
    """Reboot the system but first include some system info in the cron_log
    file and update the non-volatile copy of the file.
    """
    # wrap the reporting in a try except so that reboot is attempted for sure
    try:
        report = 'lsusb:\n%s' % subprocess.check_output('/usr/bin/lsusb')
        report += '\nls /mnt/1wire:\n%s' % subprocess.check_output(['/bin/ls', '/mnt/1wire'])
        report += '\nuptime:\n%s' % subprocess.check_output('/usr/bin/uptime')
        report += '\nfree:\n%s' % subprocess.check_output('/usr/bin/free')
        report += '\ndf:\n%s' % subprocess.check_output('/bin/df')
        report += '\nifconfig:\n%s' % subprocess.check_output('/sbin/ifconfig')
        logger.info(report)

    except:
        pass

    # backup log and Post database files before rebooting
    backup_files()

    # Update the fake hardware clock to that the time is close to right
    # after the reboot.
    subprocess.call('/sbin/fake-hwclock save', shell=True)

    # wait 5 seconds, as it seems to take this long to take effect
    time.sleep(5)

    # reboot now.  Have reworked code to that all Mini-Monitor processes
    # will kill with simple SIGTERM instead of SIGKILL.
    subprocess.call('/sbin/reboot now', shell=True)

    # wait until reboot actually occurs
    while True:
        time.sleep(1)

def backup_files():

    try:
        # Copy the application log files to a directory on the SD Card, because
        # they are on a RAM disk that will not persist a reboot.
        if os.path.exists('/var/log/pi_log.log'):
            shutil.copyfile('/var/log/pi_log.log', '/var/local/pi_log.log')
        if os.path.exists('/var/log/pi_cron.log'):
            shutil.copyfile('/var/log/pi_cron.log', '/var/local/pi_cron.log')
        if os.path.exists('/var/log/meter_reader.log'):
            shutil.copyfile('/var/log/meter_reader.log', '/var/local/meter_reader.log')

        logger.info('Backed up Log files.')

    except:
        # continue on if there is a problem with this non-essential
        # operation.
        pass

def ip_addrs():
    """Returns a list of IP addresses assigned to network interfaces on this
    system, ignoring the loopback interface.  Returns an empty list if an
    error occurs.
    """
    try:
        result = subprocess.check_output("ifconfig | grep 'inet addr' | cut -f 2 -d : | cut -f 1 -d ' '", shell=True)
        ips = [ip for ip in result.splitlines() if ip != '127.0.0.1']
    except:
        ips = []

    return ips
