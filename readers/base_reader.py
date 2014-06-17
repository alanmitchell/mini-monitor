"""Contains base Reader class that other sensor reading classes should inherit
from.
"""

# Reading Types
VALUE = 1       # continuous analog value like temperature, voltage, etc.
STATE = 2       # a reading that has discrete states, like On/Off.
COUNTER = 3     # a reading that is a cumulative count


class DummySettings:
    """An object that substitutes for the application settings module if no
    settings module is passed into the constructor of the reader object.
    Lack of a settings module generally occurs during testing of a particular
    reader.
    """
    def __init__(self):
        self.LOGGER_ID = 'test'


class Reader(object):
    
    def __init__(self, settings=None):
        """
        'settings' is the main settings module for the application.
        """
        
        # save the settings module if present, otherwise substitute a dummy
        # object with the LOGGER_ID setting.
        self._settings = settings if settings else DummySettings()
        
    def read():
        """The Reader subclass must override this method and return a list 
        (or tuple) of sensor readings.  Each sensor reading in the list should 
        be a tuple of the format:
            
            (ts, read_id, val, read_type)
            
        where 'ts' is a Unix timestamp (seconds), 'read_id' is a string that
        uniquely identifies the sensor, 'val' is the numeric sensor reading, 
        and 'read_type' is one of the reading constants listed at the top of
        this module.  An example would be:
            
            (1400883270, 'Reka_OutTemp', 72.3, VALUE)
            
        The 'read_type' controls how the readings are eventually summarized 
        when a logging interval is reached.  See the code in the logger_controller
        module for the summarization method used for each reading type.
        
        Any errors that occur and are not trapped in this method will be trapped
        and logged in the logger_controller run() method that call this read()
        method.
        """
        pass 
        