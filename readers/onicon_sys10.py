"""Contains a Reader class that reads key values from an Onicon System 10 BTU Meter.
This class subclasses the modbus_rtu.ModbusRTUreader class, which performs the Modbus
heavy lifting.  The necessity for this class is due to there being multiple registers
that need to be combined together to determine the cumulative BTUs read by the meter.

The Modbus RTU values in the settings file should be set as follows in order for this
class to work:


"""
from . import base_reader
from . import modbus_rtu

class OniconSystem10(modbus_rtu.ModbusRTUreader):

    def read(self):

        readings = super().read()

        # find the kBtu and MBtu readings in the returned list, and make a new total BTU reading.
        # delete the original readings.
        ix = 0
        for ts, sensor_id, val, reading_type_code in readings:
            if sensor_id == f'{self._settings.LOGGER_ID}_kbtu':
                kbtu = val
                kbtu_ix = ix
            if sensor_id == f'{self._settings.LOGGER_ID}_mbtu':
                mbtu = val
                mbtu_ix = ix
                mbtu_ts = ts
            ix += 1
        # delete the original kBtu and MBtu values out of the readings list.
        del readings[kbtu_ix]
        del readings[mbtu_ix]
        # make a reading that combines the MBtu and kBtu values into one floating point MBtu value.
        readings.append( (mbtu_ts, f'{self._settings.LOGGER_ID}_mbtu', mbtu + kbtu/1000.0, base_reader.VALUE) )

        return readings
