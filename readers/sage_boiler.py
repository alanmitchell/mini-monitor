#!/usr/bin/python
"""Module used with classes to read Sage Boiler Controls.
Sage21Reader class reads Sage 2.1 Boiler controls.
"""
from __future__ import division   # do floating point div even with integers
import glob, time
import minimalmodbus
import base_reader

# Set some default MODBUS settings

# More robust to close the port after each Modbus call
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

# baudrate for the Sage 2.1 controller
minimalmodbus.BAUDRATE  = 38400

# measured only 16 ms/read for a sequence of 100 regester reads, but
# to be safe, set a long timeout.
minimalmodbus.TIMEOUT  = 1.0


class Sage21Reader(base_reader.Reader):
    """Class to read sensor and status values from a Sage 2.1 Boiler Controller.
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
        device_path = glob.glob('/dev/serial/by-id/*FT232R*')[0]
        boiler = minimalmodbus.Instrument(device_path, 1)
        
        # the reading list to return.
        self.readings = []
        
        # determine the percent firing rate; it is either directly in register 8
        # or the burner fan RPM is in 8, which can be translated into % firing
        # rate.  The MSbit in the register tells which type of value is in the
        # register.
        firing_reg = boiler.read_register(8, functioncode=3)
        mask = 2**31   # mask for MSbit.
        
        if (firing_reg & mask)>0:
            # register is in tenths of percent firing rate, but remove the MSbit.
            firing_rate = (firing_reg - mask) * 0.1
        else:
            # register is in RPM.  Get max RPM to then convert to % of max.
            max_RPM = boiler.read_register(193, functioncode=3) # max heating modulation rate
            firing_rate = 100.0 * firing_reg / max_RPM   # in %, 0 - 100.0
        self.add_reading('firing_rate', firing_rate)

        # Other registers to read and record, in the form (register #, sensor name,
        # multiplier to scale register value, offset to add to scaled register value,
        # reading type constant from base_reader module).
        registers_to_read = (
            (4, 'limits', 1, 0, base_reader.STATE),
            (6, 'demand_source', 1, 0, base_reader.STATE),
            (7, 'outlet_temp', 0.18, 32.0, base_reader.VALUE),
            (10, 'flame_signal', 0.01, 0.0, base_reader.VALUE),
            (11, 'inlet_temp', 0.18, 32.0, base_reader.VALUE),
            (14, 'stack_temp', 0.18, 32.0, base_reader.VALUE),
            (16, 'ch_setpoint', 0.18, 32.0, base_reader.VALUE),
            (17, 'dhw_setpoint', 0.18, 32.0, base_reader.VALUE),
            (29, 'active_setpoint', 0.18, 32.0, base_reader.VALUE),
            (34, 'lockout_code', 1, 0, base_reader.STATE),
            (35, 'alarm_reason', 1, 0, base_reader.STATE),
            (66, 'ch_demand', 1, 0, base_reader.STATE),
            (83, 'dhw_demand', 1, 0, base_reader.STATE),
            (170, 'outdoor_temp', 0.18, 32.0, base_reader.VALUE),
            (1119, 'alarm_code', 1, 0, base_reader.STATE),
        )
        for addr, read_name, mult, offset, read_type in registers_to_read:
            val = boiler.read_register(addr, functioncode=3)
            self.add_reading(read_name, val*mult + offset, read_type)
            
        return self.readings

if __name__=='__main__':
    from pprint import pprint    
    rdr = Sage21Reader()
    pprint(rdr.read())