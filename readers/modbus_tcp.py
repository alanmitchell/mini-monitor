"""Contains a Reader class that can read values from Modbus TCP servers.

Uses the following settings from the main settings.py file:

LOGGER_ID:  Used to create the final sensor_id for each value read from the Modbus server.
MODBUS_TARGETS: Lists the Modbus Servers, Devices, and Registers that will be read.

See further documentation of these settings in the system_files/settings_template.py file.

Note: Each Modbus "sensor" will generate one Modbus read, so consider this when setting the
READ_INTERVAL setting in the settings file.
"""
import time
import struct
import logging
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import pymodbus

from . import base_reader

class ModbusTCPreader(base_reader.Reader):
    
    def read(self):

        # list to hold final readings
        readings = []

        for device_info, sensors in self._settings.MODBUS_TARGETS:

            # use the same timestamp for all of the sensors on this device
            ts = time.time()
            try:
                try:
                    host, port, kwargs = device_info
                except:
                    host, port = device_info
                    kwargs = {}
                device_addr = kwargs.get('device_addr', 1)
                endian = kwargs.get('endian', 'big')

                if endian not in ('big', 'little'):
                    raise ValueError(f'Improper endian value for Modbus device {device_info}') 

                with ModbusClient(host=host, port=port) as client:
                    for sensor_info in sensors:
                        try:
                            try:
                                register, sensor_name, kwargs = sensor_info
                            except:
                                register, sensor_name = sensor_info
                                kwargs = {}
                            
                            datatype = kwargs.get('datatype', 'uint16')
                            transform = kwargs.get('transform', None)
                            register_type = kwargs.get('register_type', 'holding')
                            reading_type = kwargs.get('reading_type', 'value')

                            # determine number of registers to read and the correct struct
                            # unpacking code based upon the data type for this sensor.
                            try:
                                reg_count, unpack_fmt = {
                                    'uint16': (1, 'H'),
                                    'int16': (1, 'h'),
                                    'uint32': (2, 'I'),
                                    'int32': (2, 'i'),
                                    'float': (2, 'f'),
                                    'float32': (2, 'f'),
                                    'double': (4, 'd'),
                                    'float64': (4, 'd'),
                                }[datatype]
                            except:
                                logging.exception(f'Invalid Modbus Datatype: {datatype} for Sensor {sensor_info}')
                                continue

                            # Determine the correct function to use for reading the values
                            try:
                                read_func = {
                                    'holding': client.read_holding_registers,
                                    'input': client.read_input_registers,
                                    'coil': client.read_coils,
                                    'discrete': client.read_discrete_inputs
                                    }[register_type]
                            except:
                                logging.exception(f'Invalid Modbus register type for Sensor {sensor_info}')
                                continue

                            try:
                                reading_type_code = {
                                    'value': base_reader.VALUE,
                                    'state': base_reader.STATE,
                                    'counter': base_reader.COUNTER
                                }[reading_type]
                            except:
                                logging.exception(f'Invalid Reading Type for Sensor {sensor_info}')
                                continue


                            result = read_func(register, reg_count, unit=device_addr)
                            if not hasattr(result, 'registers'):
                                raise ValueError(f'An error occurred while reading Sensor {sensor_info} from Modbus Device {device_info}')
                            
                            # make an array of register values with least-signifcant value first
                            registers = result.registers

                            # calculate the integer equivalent of the registers read
                            if endian == 'big':
                                registers = reversed(registers)
                            val = 0
                            mult = 1
                            for reg in registers:
                                val += reg * mult
                                mult *= 2**16

                            # Use the struct module to convert this number into the appropriate data type.
                            # First, create a byte array that encodes this unsigned number according to 
                            # how many words it contains.
                            reg_count_to_pack_fmt = {
                                1: 'H',
                                2: 'I',
                                4: 'Q'
                            }
                            pack_fmt = reg_count_to_pack_fmt[reg_count]
                            packed_bytes = struct.pack(pack_fmt, val)
                            # unpack bytes to convert to correct datatype
                            val = struct.unpack(unpack_fmt, packed_bytes)[0]

                            if transform:
                                val = eval(transform)
                            sensor_id = f'{self._settings.LOGGER_ID}_{sensor_name}'
                            readings.append( (ts, sensor_id, val, reading_type_code) )                                

                        except Exception as err:
                            logging.exception(str(err))
                            continue    # on to next sensor

            except Exception as err:
                logging.exception(str(err))
                continue   # on to next device

        return readings
