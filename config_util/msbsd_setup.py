#!/usr/bin/python

'''Utility to configure WiFi Gas Meter Readers for the
Mat-Su School District.
'''

from distutils.util import strtobool
import io
import setup_utils

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

meter_ids = raw_input('Enter Gas Meter ID or multiple IDs separated by commas: ')
file_contents = open('pi_logger/settings.py').read()
file_contents = setup_utils.replace_setting(file_contents, 'METER_IDS', '[%s]' % meter_ids)
with io.open('pi_logger/settings.py', 'w', newline='\n') as f:
    f.write(unicode(file_contents))
