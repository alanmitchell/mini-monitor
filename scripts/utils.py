import subprocess
import logging
import time
import cron_logging


def reboot():
    """Reboot the system but first include some system info in the cron_log
    file.
    """
    # wrap the reporting in a try except so that reboot is attempted for sure
    try:
        report = 'lsusb:\n%s' % subprocess.check_output('/usr/bin/lsusb')
        report += '\nls /mnt/1wire:\n%s' % subprocess.check_output(['/bin/ls', '/mnt/1wire'])
        report += '\nuptime:\n%s' % subprocess.check_output('/usr/bin/uptime')
        report += '\nfree:\n%s' % subprocess.check_output('/usr/bin/free')
        report += '\ndf:\n%s' % subprocess.check_output('/bin/df')
        report += '\nifconfig:\n%s' % subprocess.check_output('/sbin/ifconfig')
        logging.info(report)
    except:
        pass

    subprocess.call('/sbin/shutdown -r now', shell=True)

    # wait until reboot actually occurs
    while True:
        time.sleep(1)


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
