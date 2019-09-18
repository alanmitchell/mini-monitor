#!/usr/bin/env python3
"""Module used to read temperature sensors connected to the thermistor board
on a Labjack U3.
"""
import time
from . import base_reader, myU3, thermistor


def readTemp(dev, th, ch, vref):
    """Returns a temperature value from a thermistor connected to a Labjack U3
    device.
    'dev' is an open MyU3 Labjack device object.
    'th' is a Thermistor object, appropriate for the connected thermistor.
    'ch' is the U3 Analog channel number (0 - 15).
    'vref' is the voltage of the voltage source used in the thermistor divider
        circuit.
    If the channel is open or shorted, the value None is returned.
    """
    # read the voltage across the thermistor
    v = dev.getAvg(ch)
    
    # Return None if the channel is open or shorted, otherwise calculate and
    # return the temperature value.
    if v < 0.02 * vref or v > 0.98 * vref:
        return None
    else:
        return th.TfromV(v, vref)


class LabjackTempReader(base_reader.Reader):
    """Class to read temperature values connected to the thermistor board on a
    Labjack U3 data acquisition device.  Reads all thermistor channels (EIO0 - 
    EIO6, plus it is assumed that channels A, B, and C on the thermistor board
    are connected to FIO0-FIO2.
    """
    
    def read(self):
        """Read the temperature values and return in a list.
        """

        try:
            # make the thermistor object. assumes use of BAPI 10K-3 thermistors
            # and a 20k divider resistor.            
            therm = thermistor.Thermistor('BAPI 10K-3', dividerR=20000)
            
            # open Labjack device and configure Analog inputs.
            dev = myU3.MyU3()
            dev.configIO(EIOAnalog=0xFF, FIOAnalog=0x07)
            
            # With the thermistor board, the voltage reference supplying the 
            # divider circuit is connected to EIO7, which is Analog channel 15.
            v_ref = dev.getAvg(15)
            
            # List of readings
            reads = []
            
            # create a list of analog channels to read with their associated 
            # channel names.
            channels = [(8+i, 'EIO%d_temp' % i) for i in range(7)]
            channels += [(0, 'A_temp'), (1, 'B_temp'), (2, 'C_temp')]
        
            # read the channels and fill out the reading list.
            tm = time.time()   # current time
            for ch, nm in channels:
                temp = readTemp(dev, therm, ch, v_ref)
                if temp is not None:
                    sensor_id = '%s_%s' % (self._settings.LOGGER_ID, nm)                    
                    reads.append( (tm, sensor_id, temp, base_reader.VALUE) )
            
            # read the internal temperature of the labjack and append
            temp_lj = (dev.getTemperature() - 273.15)*1.8 + 32.0
            reads.append( (tm, '%s_lj_temp' % self._settings.LOGGER_ID, temp_lj, base_reader.VALUE) )

            return reads
            
        except:
            # re-raise the error to be caught in the calling routine.
            raise
            
        finally:
            # always want to close Labjack.
            dev.close()
                        

if __name__=='__main__':
    from pprint import pprint    
    rdr = LabjackTempReader()
    pprint(rdr.read())