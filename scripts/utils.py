import subprocess
import logging
import time
import os
import shutil
import sqlite3
import scripts.cron_logging

# get the logger for the application
logger = scripts.cron_logging.logger

def reboot():
    """Reboot the system but first include some system info in the cron_log
    file and update the non-volatile copy of the file.
    """
    # wrap the reporting in a try except so that reboot is attempted for sure
    try:
        report = 'lsusb:\n%s' % subprocess.check_output('/usr/bin/lsusb', text=True)
        report += '\nls /mnt/1wire:\n%s' % subprocess.check_output(['/bin/ls', '/mnt/1wire'], text=True)
        report += '\nuptime:\n%s' % subprocess.check_output('/usr/bin/uptime', text=True)
        report += '\nfree:\n%s' % subprocess.check_output('/usr/bin/free', text=True)
        report += '\ndf:\n%s' % subprocess.check_output('/bin/df', text=True)
        report += '\nifconfig:\n%s' % subprocess.check_output('/sbin/ifconfig', text=True)
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
        if os.path.exists('/var/log/mosquitto.log'):
            shutil.copyfile('/var/log/mosquitto.log', '/var/local/mosquitto.log')
        if os.path.exists('/var/log/mqtt_to_bmon.log'):
            shutil.copyfile('/var/log/mqtt_to_bmon.log', '/var/local/mqtt_to_bmon.log')

        logger.info('Backed up Log files.')

    except:
        # continue on if there is a problem with this non-essential
        # operation.
        pass

    try:
        # Copy the reading post queue from the RAM disk to non-volatile
        # storage.
        # Before copying the database file, need to force a lock on it so that no
        # write operations occur during the copying process

        fname = '/var/run/postQ.sqlite'
        fname_bak = '/var/local/postQ.sqlite'   # non-volatile
        conn = sqlite3.connect(fname)
        cursor = conn.cursor()

        # create a dummy table to write into.
        try:
            cursor.execute('CREATE TABLE _junk (x integer)')
        except:
            # table already existed
            pass

        # write a value into the table to create a lock on the database
        cursor.execute('INSERT INTO _junk VALUES (1)')

        # now copy database
        shutil.copy(fname, fname_bak)

        # Rollback the Insert as we don't really need it.
        conn.rollback()
        conn.close()

        logger.info('Backed up Post database.')

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
        ips = []
        result = subprocess.check_output('ifconfig | grep "inet "', shell=True, text=True)
        for lin in result.splitlines():
            flds = lin.strip().split(' ')
            if flds[1] != '127.0.0.1':
                ips.append(flds[1])
    except:
        ips = []

    return ips
