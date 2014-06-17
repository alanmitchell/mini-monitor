#!/usr/bin/python
"""Reader module for reporting information about the operation
of the monitoring system.
"""
import time
import base_reader

class SysInfo(base_reader.Reader):
    
    def read(self):

        # Use the ID of this logger to create a unique ID.
        sensor_id = '%s_uptime' % (self._settings.LOGGER_ID)
        
        # parse seconds of uptime out of proc file.
        secs = float( open('/proc/uptime').read().split()[0] )

        return [(time.time(), sensor_id, int(secs), base_reader.COUNTER)]

if __name__=='__main__':
    from pprint import pprint    
    rdr = SysInfo()
    pprint(rdr.read())