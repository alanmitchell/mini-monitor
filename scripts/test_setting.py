#!/usr/bin/python3
"""Script to test a setting in the mini-monitor settings file.
"""
import sys
import argparse

# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
from settings import *

parser = argparse.ArgumentParser()
parser.add_argument("setting_expr", help="the settings expression to test")
args = parser.parse_args()

expr = args.setting_expr

# if the test is True, then exit with 0, a success value.  Otherwise
# exit with 1.  An error will naturally exit with a non-zero exit code.
if eval(expr):
    sys.exit(0)
else:
    sys.exit(1)
