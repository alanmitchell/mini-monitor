#!/usr/bin/python

'''Utility to configure WiFi Gas Meter Readers for the
Mat-Su School District.
'''

from distutils.util import strtobool
import io
import os
import re
import setup_utils

THIS_DIR = os.path.dirname(__file__)

logger_id = raw_input('Enter a short (15 char max) name for this site (no spaces): ')
logger_id = logger_id.replace(' ', '')

# read settings file so it can be modified
settings_fn = os.path.join(THIS_DIR, 'pi_logger/settings.py')
file_contents = open(settings_fn).read()
file_contents = setup_utils.replace_line(file_contents, r'LOGGER_ID\s*=', 'LOGGER_ID = "%s"' % logger_id)

meter_ids = raw_input('Enter Gas Meter ID or multiple IDs separated by commas: ')
file_contents = setup_utils.replace_line(file_contents, r'METER_IDS\s*=', 'METER_IDS = [%s]' % meter_ids)

# loop through the common file containing other settings and
# substitute.
common_fn = os.path.join(THIS_DIR, 'common_settings_sample.txt')
for line in open(common_fn):
    if re.search(r'^\s*#', line) is None:
        flds = line.split('\t')
        if len(flds)==2:
            print flds
            file_contents = setup_utils.replace_line(file_contents, flds[0].strip(), flds[1].strip())

# Write the revised settings file.
with io.open(settings_fn, 'w', newline='\n') as f:
    f.write(unicode(file_contents))

# Configure WiFi, if requested.
error = True
while error:
    try:
        if strtobool(raw_input('Use WiFi for Internet? (y/n): ')):
            ssid = raw_input('Enter the SSID of the WiFi network: ')
            psk = raw_input('Enter the Password of the WiFi network: ')
            file_contents = setup_utils.wpa_sup_file(ssid=ssid, psk=psk)
        else:
            file_contents = setup_utils.wpa_sup_file()
        error = False
    except:
        print 'Entry must be y or n!'

with io.open('pi_logger/wpa_supplicant.conf', 'w', newline='\n') as f:
    f.write(unicode(file_contents))

