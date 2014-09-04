#!/usr/bin/python
"""Module used with classes to read Aerco Boiler Controls.
"""
from __future__ import division   # do floating point div even with integers
import time, logging
import minimalmodbus
import base_reader

# Set some default MODBUS settings

# More robust to close the port after each Modbus call
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

# baudrate for the Sage 2.1 controller
minimalmodbus.BAUDRATE  = 9600

# Manual indicates need to wait 2 seconds for boiler to respond.  Wait a bit
# longer than that.
minimalmodbus.TIMEOUT  = 2.5

def try_read(instrument, register, function_code=4, times=3):
    """Tries to read the 'register' of the 'instrument' up to 'times' times 
    if need be because of read errors.  If no successful tries occurred 
    an error is raised.
    """
    for i in range(times):
        try:
            val = instrument.read_register(register, functioncode=function_code)
            time.sleep(0.05)
            return val
        except:
            if i == (times-1):
                # final try, give up and raise the exception
                raise
            else:
                # delay and try again
                time.sleep(0.1)


class BMS2reader(base_reader.Reader):
    """Class to read sensor and status values from a BMS II Boiler controller
    """
    
    def add_reading(self, rd_name, rd_val, rd_type=base_reader.VALUE):
        """Adds a reading to the self.readings list of readings.  Add the 
        proper logger ID prefix to the reader name from the settings module.
        """
        sensor_id = '%s_%s' % (self._settings.LOGGER_ID, rd_name)
        self.readings.append( (time.time(), sensor_id, rd_val, rd_type) )
        
    
    def read(self):
        """Read values from the boiler control and return in a list.
        """
        
        # I think it is more robust to find the RS-485 converter and make
        # a minimalmodbus Instrument object upon each call to the read() method.
        
        # find the device file for the FTDI RS-485 converter, and make an
        # Instrument object.
        device_path = base_reader.Reader.available_ftdi_ports[0]
        boiler = minimalmodbus.Instrument(device_path, 128)
        
        # the reading list to return.
        self.readings = []
        
        # Get firing rate and total boilers fired 
        try:
            firing_rate = try_read(boiler, 4)
            self.add_reading('firing_rate', firing_rate, base_reader.VALUE)
            boilers_fired = try_read(boiler, 7)
            # use STATE type reading so every change of this value is recorded.
            self.add_reading('boilers_fired', boilers_fired, base_reader.STATE)
            self.add_reading('firing_rate_tot', firing_rate * boilers_fired, base_reader.VALUE)
        except:
            logging.exception('Error reading firing info.')
        
        # Other registers to read and record, in the form (register #, sensor name,
        # multiplier to scale register value, offset to add to scaled register value,
        # reading type constant from base_reader module).
        registers_to_read = (
            (1, 'header_temp', 1, 0, base_reader.VALUE),
            (2, 'outdoor_temp', 1, 0, base_reader.VALUE),
            (5, 'header_setpoint', 1, 0, base_reader.VALUE),
            (8, 'boilers_online', 1, 0, base_reader.STATE),
            (10, 'fault_code', 1, 0, base_reader.STATE),
            (16, 'lead_boiler', 1, 0, base_reader.STATE),
            (25, 'boiler1_status', 1, 0, base_reader.STATE),
            (26, 'boiler2_status', 1, 0, base_reader.STATE),
            (57, 'io_status', 1, 0, base_reader.STATE),
        )
        for addr, read_name, mult, offset, read_type in registers_to_read:
            try:
                val = try_read(boiler, addr)
                self.add_reading(read_name, val*mult + offset, read_type)
            except:
                logging.exception('Error reading register %s of BMS II.' % addr)
            
        return self.readings

if __name__=='__main__':
    from pprint import pprint    
    rdr = BMS2reader()
    pprint(rdr.read())