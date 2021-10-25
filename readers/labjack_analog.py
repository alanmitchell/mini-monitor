#!/usr/bin/env python3
"""Reads the first four Analog input channels on a Labjack U3.
"""
import time
from . import base_reader, myU3

class LabjackAnalog(base_reader.Reader):
    """Class to read analog channels AIN0 through AIO3 on a Labjack U3.
    """
    
    def read(self):
        """Read the voltage values and return in a list.
        """

        try:

            # open Labjack device
            dev = myU3.MyU3()
                        
            # List of readings
            reads = []
            
            # read the channels and fill out the reading list.
            tm = time.time()   # current time
            for ch in range(4):
                volts = dev.getAvg(ch)
                # Don't report channels that are grounded
                if volts >= 0.03:
                    sensor_id = f'{self._settings.LOGGER_ID}_ain{ch}'                    
                    reads.append( (tm, sensor_id, volts, base_reader.VALUE) )

            return reads
            
        except:
            # re-raise the error to be caught in the calling routine.
            raise
            
        finally:
            # always want to close Labjack.
            dev.close()
                        

if __name__=='__main__':
    from pprint import pprint    
    rdr = LabjackAnalog()
    pprint(rdr.read())
