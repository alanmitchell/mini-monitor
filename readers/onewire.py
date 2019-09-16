#!/usr/bin/python
"""Module used to read devices on a Dallas 1-wire bus using the OWFS library
(see owfs.org).  The class the does the reading of the bus is OneWireReader.
"""
import logging, glob, os, time
from . import base_reader

MNT_POINT = '/mnt/1wire'

def ds2406(rd_val):
    """Converts the sensed.A file value of the DS2406 to one integer digital
    reading.
    """
    return [ (int(rd_val), '') ]
    
def ds2423(rd_val):
    """Converts the counter.ALL file value of the DS2423 dual counter to an
    A and a B counter reading.
    """
    a_ct, b_ct = rd_val.split(',')
    return [ (int(a_ct), 'A'), (int(b_ct), 'B') ]

# Dictionary that contains info about how to read various 1-wire sensors.
# The keys are Family Codes for the sensors handled by this system; the values 
# are 4-tuples of the format (reading type from the 'base_reader' module, file 
# name in the OWFS file system to read the current value of the sensor, function 
# used to convert the read value into a set of readings, True/False value that
# if True reads the sensor from the 'uncached' OWFS directory, forcing an actual
# read of the sensor instead of using a cached value).  If there is no 
# conversion function, the read value from the file is converted to a floating 
# point value by applying the Python 'float' function to the contents of the
# OWFS file.  If there is a conversion function, it must return a list of
# 2-tuples of the form: (sensor value, ID suffix); this accomodates chips with 
# multiple channels.  The 'ID suffix' is appended to the unique 1-wire ID of the 
# sensor chip to create a unique identifier for the channel; the 1-wire ID and 
# the suffix are separated by a period.
FAMILY_INFO = {
'28': (base_reader.VALUE, 'temperature10', None, False),   # DS18B20
'10': (base_reader.VALUE, 'temperature', None, False),     # DS18S20
'22': (base_reader.VALUE, 'temperature10', None, False),   # DS1822
'12': (base_reader.STATE, 'sensed.A', ds2406, True),      # DS2406, read from uncached
'1D': (base_reader.COUNTER, 'counter.ALL', ds2423, True), # DS2423 dual counter from uncached
}

class OneWireReader(base_reader.Reader):
    """Class that reads the sensors on the 1-wire bus.  The read() method
    performs the read action.  The OWFS 1-wire library is used.
    """
    
    def __init__(self, settings=None):
        """'settings' is the general settings file for the application.
        """
        # Call constructor of base class
        super(OneWireReader, self).__init__(settings)
        
        # Set some one-wire settings.
        # Increasing the cache life below keeps read times shorter, which are
        # important for detecting state changes on one-wire digial I/O devices.
        onewire_settings = ( ('units/temperature_scale', 'F'),
                     ('timeout/volatile', '30'),
                     ('timeout/directory', '120'),
                     ('timeout/presence', '240'),
                   )
        for fname, val in onewire_settings:
            try:
                open(os.path.join(MNT_POINT, 'settings', fname), 'w').write(val)
            except:
                logging.exception('Error initializing one-wire setting %s' % fname)
            
    
    def read(self):
        """Read the 1-wire sensors matching family codes in the FAMILY_INFO
        dictionary.  Returns a list of readings (perhaps multiple readings for
        one sensor if it has multiple channels).  The reading list consists of
        4-tuples of the form (UNIX timestamp in seconds, reading ID string, 
        reading value, reading type which is a value from the 'base_reader' module.
        """
        
        # the reading list to return.
        readings = []
        
        # loop through all the 1-wire devices at the OWFS mount point
        for fname in glob.glob(os.path.join(MNT_POINT, '??.*')):
            try:
                one_wire_id = os.path.basename(fname)
                family_code = one_wire_id.split('.')[0]
                if family_code in FAMILY_INFO:
                    # get the reading info about this family code.
                    read_type, val_file, convert_func, uncached = FAMILY_INFO[family_code]
                    
                    # create a filename that holds the value data for the sensor.
                    # this filename depends on whether we are reading the cached 
                    # or uncached value.
                    read_fname = os.path.join(MNT_POINT, 'uncached', one_wire_id, val_file) if uncached \
                        else os.path.join(fname, val_file)
                    value_data = open(read_fname).read()
                    
                    # apply the conversion function to parse the file data
                    if convert_func:
                        values = convert_func(value_data)
                    else:
                        values = [ (float(value_data), '') ]
    
                    # add the readings from this sensor to the list
                    ts = time.time()
                    for val, suffix in values:
                        read_id = '%s.%s' % (one_wire_id, suffix) if len(suffix) else one_wire_id
                        readings.append( (ts, read_id, val, read_type) )
            except:
                logging.exception('Error reading 1-wire sensor %s' % fname)

        return readings

if __name__=='__main__':
    from pprint import pprint
    reader = OneWireReader()
    pprint(reader.read())