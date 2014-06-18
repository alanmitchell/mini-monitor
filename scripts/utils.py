import subprocess, logging
import cron_logging

def reboot():
    """Reboot the system but first include some system info in the cron_log
    file.
    """
    report = 'lsusb:\n%s' % subprocess.check_output('lsusb')
    report += '\nls /mnt/1wire:\n%s' % subprocess.check_output(['ls', '/mnt/1wire'])
    report += '\nuptime:\n%s' % subprocess.check_output('uptime')
    report += '\nfree:\n%s' % subprocess.check_output('free')
    report += '\ndf:\n%s' % subprocess.check_output('df')
    report += '\nifconfig:\n%s' % subprocess.check_output('ifconfig')
    logging.info(report)
    
    subprocess.call('/sbin/shutdown -r now', shell=True)
