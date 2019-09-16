#!/usr/bin/env python
"""Reader module for reading one 1-Wire temperature sensor connected to a 
DS9097 1-wire adapter connected to /dev/ttyUSB0 on the Raspberry Pi.  This
uses the DigiTemp command line program, https://www.digitemp.com/, to read
the sensor.
This was developed for Marco Castillo's Enstar project.
"""
import time
import subprocess
from . import base_reader

# The name of the digitemp Program being used.
# This depends on the 1-wire master being used, and choices are:
# digitemp_DS2490, digitemp_DS9097, and digitemp_DS9097U
DIGITEMP_CMD = 'digitemp_DS9097'

# The serial port being used by the 1-wire adapter
SERIAL_PORT = '/dev/ttyUSB0'

class USBtemperature1(base_reader.Reader):

    def __init__(self, settings=None):
        """'settings' is the general settings file for the application.
        """
        # Call constructor of base class
        super(USBtemperature1, self).__init__(settings)

        # Run the intialization for the DigiTemp program, which finds the sensors
        # and writes a configuration file .digitemprc in the current directory.
        subprocess.check_call('%s -i -s %s' % (DIGITEMP_CMD, SERIAL_PORT), shell=True)

    def read(self):

        # read the attached sensor(s).  Assume the last sensor in the list is the
        # temperature sensor. This reader is meant to be used with one sensor attached,
        # thus justifying the assumption.
        result = subprocess.check_output('%s -a' % DIGITEMP_CMD, shell=True)
        last_line = result.splitlines()[-1]
        temperature_value = float(last_line.split()[-1])

        # Use the ID of this logger to create a unique ID.
        sensor_id = '%s_usb_temperature' % (self._settings.LOGGER_ID)

        # Timestamp of current state
        ts = time.time()

        readings = [(ts, sensor_id, temperature_value, base_reader.VALUE)]

        return readings


if __name__ == '__main__':
    # This script can be run directly for testing.
    from pprint import pprint

    rdr = USBtemperature1()
    pprint(rdr.read())