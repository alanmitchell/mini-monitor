#!/usr/bin/python
"""Run by cron every 15 minutes.
"""
import subprocess, time, logging
import cron_logging

# check to see if the network is working.  If not, kill wvdial and restart it.
try:
    subprocess.check_output(['/usr/bin/nslookup', 'gci.net'])
except:
    # if nslookup returns non-zero error code, an exception is raised
    logging.error('No network connection. Restarting cellular modem.')
    subprocess.call('/home/pi/pi_logger/scripts/start_cell_internet.py', shell=True)
