#!/usr/bin/python
"""Runs via cron every day.
"""
import subprocess, datetime, logging
import cron_logging

REBOOT_DAYS = 3   # Number of days between forced reboots

# reboot every three days
if datetime.datetime.now().day % REBOOT_DAYS == 0:
    logging.info('Reboot every %s days occurring now.' % REBOOT_DAYS)
    subprocess.call('/sbin/shutdown -r now', shell=True)

