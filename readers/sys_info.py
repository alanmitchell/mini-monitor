#!/usr/bin/python
"""Reader module for reporting information about the operation
of the monitoring system.
"""
import time
import base_reader

class SysInfo(base_reader.Reader):
    
    def read(self):

        # Uptime reading
        # Use the ID of this logger to create a unique ID.
        sensor_id = '%s_uptime' % (self._settings.LOGGER_ID)
        
        # parse seconds of uptime out of proc file.
        secs = float( open('/proc/uptime').read().split()[0] )
        
        ts = time.time()

        readings = [(ts, sensor_id, int(secs), base_reader.COUNTER)]
        
        # CPU Temperature
        sensor_id = '%s_cpu_temp' % (self._settings.LOGGER_ID)
        cpu_temp = float(open('/sys/class/thermal/thermal_zone0/temp').read())/1000.0
        if cpu_temp > -50.0 and cpu_temp < 150.0:
            readings.append( (ts, sensor_id, cpu_temp, base_reader.VALUE) )
            
        return readings

if __name__=='__main__':
    from pprint import pprint    
    rdr = SysInfo()
    pprint(rdr.read())