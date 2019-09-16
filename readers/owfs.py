#!/usr/bin/python
"""Module used to read Maxim 1-Wire sensors using the OWFS software.
OWFS must be installed and configured, as shown here and in other tutorials:
https://www.packtpub.com/books/content/raspberry-pi-and-1-wire
http://www.sheepwalkelectronics.co.uk/RPI2_software.php
"""
   # do floating point div even with integers
import time
import subprocess
from . import base_reader

class OWFSreader(base_reader.Reader):
    """Class to read values from the OWFS system.
    """

    def read(self):
        """Read OWFS sensor values and return.
        """
        readings = []
        ts = time.time()

        for dev in subprocess.check_output(['owdir']).splitlines():
            if dev.startswith('/28.'):
                try:
                    val = subprocess.check_output(['owread', '/uncached%s/temperature' % dev])
                    val = float(val)*1.8 + 32.0    # convert to deg F
                    readings.append(
                        [ts, '%s_%s' % (self._settings.LOGGER_ID, dev[1:]), val, base_reader.VALUE]
                    )
                except:
                    # just move on to next sensor
                    pass

        return readings

if __name__=='__main__':
    from pprint import pprint    
    rdr = OWFSreader()
    pprint(rdr.read())
