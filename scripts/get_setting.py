#!/usr/bin/python
"""Script to get a setting in the mini-monitor settings file and write it
to stdout so that it can be used in a shell script.
"""
import sys
import argparse

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

parser = argparse.ArgumentParser()
parser.add_argument("setting_name", help="the name of the setting to retrieve")
args = parser.parse_args()

setting_name = args.setting_name
setting_value = settings.__dict__[setting_name]
sys.stdout.write(str(setting_value))
