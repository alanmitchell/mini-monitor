#!/usr/bin/python
"""Module used to read Maxim 1-Wire sensors using the OWFS software.
OWFS must be installed and configured, as shown here and in other tutorials:
http://www.sheepwalkelectronics.co.uk/RPI2_software.php
"""
from __future__ import division   # do floating point div even with integers
import time
import subprocess
import base_reader

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
                    val = float(val)
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
