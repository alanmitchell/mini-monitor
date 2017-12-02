#!/usr/bin/python
"""Module used with classes to read the sensors on the Room Energy
Add-on board: temperature, humidity, light and CO2.
"""
from __future__ import division   # do floating point div even with integers
import time
import smbus
import base_reader
import lib.tsl2591

def co2(i2c_bus):
    i2c_bus.write_i2c_block_data(0x15, 0x04, [0x13, 0x8B, 0x00, 0x01])
    time.sleep(2)
    data = i2c_bus.read_i2c_block_data(0x15, 0x00, 4)
    msb = data[2]
    lsb = data[3]
    return (((msb & 0x3F) << 8) | lsb)

class RoomEnergyReader(base_reader.Reader):
    """Class to read values from the Room Energy Monitor.
    """

    def read(self):
        """Read values from the Room Energy Monitor board and
        return as a list.
        """

        # Get I2C bus
        bus = smbus.SMBus(1)

        # SHT31 address, 0x44(68)
        # Send measurement command, 0x2C(44)
        #               0x06(06)        High repeatability measurement
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])

        time.sleep(0.5)

        # SHT31 address, 0x44(68)
        # Read data back from 0x00(00), 6 bytes
        # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        data = bus.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        temp = data[0] * 256 + data[1]
        temp_F = -49 + (315 * temp / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        #tsl = lib.tsl2591.Tsl2591()
        #full, ir = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
        #lux = tsl.calculate_lux(full, ir)  # convert raw values to lux

        # Read the CO2
        co2_ppm = co2(bus)

        ts = time.time()

        return [ (ts, '%s_rm_temp' % self._settings.LOGGER_ID, temp_F, base_reader.VALUE),
                 (ts, '%s_rm_humid' % self._settings.LOGGER_ID, humidity, base_reader.VALUE),
                 #(ts, '%s_rm_light' % self._settings.LOGGER_ID, lux, base_reader.VALUE),
                 (ts, '%s_rm_co2' % self._settings.LOGGER_ID, co2_ppm, base_reader.VALUE),
        ]

if __name__=='__main__':
    from pprint import pprint    
    rdr = RoomEnergyReader()
    pprint(rdr.read())
