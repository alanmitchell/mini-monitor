"""Contains a Reader class that reads key values from an Onicon System 10 BTU Meter.
This class subclasses the modbus_rtu.ModbusRTUreader class, which performs the Modbus
heavy lifting.  The necessity for this class is due to there being multiple registers
that need to be combined together to determine the cumulative BTUs read by the meter.

For Modbus register documentation
See https://www.onicon.com/wp-content/uploads/0653-13-System-10-MOD-Network-Interface-Installation-Guide-for-email-07-18.pdf
remember to subtract 1 from register address, because pymodbus wants an offset address from first
register

The Modbus RTU values in the settings file should be set as follows in order for this
class to work:
ONICON_ADDR = 17       # Modbus address of the Onicon meter. Default is 17
rtu_device1 = ('/dev/ttyUSB0', ONICON_ADDR)      # substitute the proper serial port
d1_sensors = (
    (10, 'flow', dict(transform='val/60')),                       # GPH / 60 will give GPM with good resolution
    (21, 'temp_supply', dict(transform='val/100')),
    (22, 'temp_return', dict(transform='val/100')),
    (25, 'kbtu', dict(reading_type='counter')),
    (26, 'mbtu', dict(reading_type='counter')),
    (27, 'gbtu', dict(reading_type='counter')),
)

# Here is the required Settings variable to use the Modbus RTU reader.  The above variables
# were just used to make a clearer presentation.
MODBUS_RTU_TARGETS = (
    (rtu_device1, d1_sensors),
)

The only critical names are "gbtu", "kbtu" and "mbtu" for this class to work.  Temperature and flow variables
could be named differently.
"""

from . import base_reader
from . import modbus_rtu

class OniconSystem10(modbus_rtu.ModbusRTUreader):

    def read(self):

        readings = super().read()

        # find the kBtu, MBtu, & GBtu readings in the returned list, and make a new total BTU reading.
        # delete the original readings.
        for reading in readings:
            ts, sensor_id, val, reading_type_code = reading
            if sensor_id == f'{self._settings.LOGGER_ID}_kbtu':
                kbtu = val
                kbtu_rdg = reading
            if sensor_id == f'{self._settings.LOGGER_ID}_mbtu':
                mbtu = val
                mbtu_rdg = reading
                mbtu_ts = ts
            if sensor_id == f'{self._settings.LOGGER_ID}_gbtu':
                gbtu = val
                gbtu_rdg = reading
        # delete the original kBtu, MBtu & GBtu values out of the readings list.
        readings.remove(kbtu_rdg)
        readings.remove(mbtu_rdg)
        readings.remove(gbtu_rdg)

        # make a reading that combines the MBtu and kBtu values into one floating point MBtu value.
        # Put this value in twice so that a Btu/hour rate sensor can be created and a sensor that shows
        # the cumulative energy count can be shown.
        mbtu_float = gbtu*1000. + mbtu + kbtu/1000.0
        readings.append( (mbtu_ts, f'{self._settings.LOGGER_ID}_mbtu', mbtu_float, base_reader.COUNTER) )
        readings.append( (mbtu_ts, f'{self._settings.LOGGER_ID}_mbtu_total', mbtu_float, base_reader.COUNTER) )

        return readings

if __name__ == "__main__":
    # Just to see if all packages are present and syntax passes.
    print('Testing Onicon System 10 imports and syntax.')
    rdr = OniconSystem10()
