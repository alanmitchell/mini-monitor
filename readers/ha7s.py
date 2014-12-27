#!/usr/bin/python
"""Module used to read devices on a Dallas 1-wire bus with an Embedded
Devices HA7S master.
The class that does the reading of the bus is HA7Sreader.
"""
import logging, time, re, glob
import serial
import base_reader

# ----------- Dallas 1-wire CRC Calculations -------------

crc8_table = [
0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53]

def crc8_is_OK(hex_string):
    """Returns True if the hex_string ending in a CRC byte passes the
    Dallas 1-wire CRC8 check.
    Code adapted from:  https://forum.sparkfun.com/viewtopic.php?p=51145.
    """
    # break the Hex string into a list of bytes
    byte_list = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]
    val = 0
    for x in byte_list:
        val = crc8_table[val ^ x]
    # answer should be 0 if the byte string is valid
    return val==0


def crc16_is_OK(hex_string):
    """Returns True if the hex_string ending in two CRC16 bytes passes
    the Dallas 1-wire CRC16 check.
    Code adapted from:  http://forum.arduino.cc/index.php?topic=37648.0;wap2
    """
    # break the Hex string into a list of bytes
    byte_list = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]
    crc = 0
    for inbyte in byte_list:
        for j in range(8):
            mix = (crc ^ inbyte) & 0x01
            crc = crc >> 1
            if mix:
                crc = crc ^ 0xA001
            inbyte = inbyte >> 1;

    return crc==0xB001

# --------- End CRC Calculations ---------------

class HA7_port(serial.Serial):
    '''Class representing a Serial Port with an HA7S connected to it.  Subclass of the
    standard pySerial serial port class, so all of the pySerial port methods are
    available as well.  This class implements some basic methods for communicating
    with the HA7S.
    '''
    
    def __init__(self, port_name):
        '''Open the port using the 'port_name' port, e.g. 'COM29', '/dev/ttyUSB0'.
        '''
        super(HA7_port, self).__init__(port_name, baudrate=9600, timeout=0.2)
        
    def readline(self):
        '''Overrides the pySerial readline() method, because that metho reads until
        a \n is received.  Instead, this method reads until a <CR> is received and 
        returns the results, *not* including the <CR>.  Also returns if a read timeout 
        occurs.
        '''
        ret = ''
        while True:
            c = self.read(1)
            if len(c)==0 or c=='\r':
                return ret
            ret += c
    
    def reset(self):
        '''Issues a one-wire reset command.  Returns nothing.
        '''
        self.write('R')
        self.readline()

    regex_dev = re.compile('^[0-9A-F]{16}$')
    def device_list(self):
        '''Returns a list of devices found on the one-wire bus.
        Each item in the returned list is a dictionary with characteristics
        of the found device.
        '''
        self.flushInput()
    
        # list of devices found
        dev_list = []
        # find the first device
        self.write('S')
        lin = self.readline()
        while HA7_port.regex_dev.search(lin):
            rec = {}
            
            # unreverse the address
            rec['addr'] = ''
            for i in range(0, 16, 2):
                rec['addr'] += lin[14-i:14-i+2]
    
            # only add this to the list if the CRC passes
            if crc8_is_OK(rec['addr']):
                rec['family'] = lin[-2:]   # family code
                # make the id in the format used by the BMS system
                rec['id'] = '%s.%s' % (rec['family'], rec['addr'][2:-2])
                dev_list.append(rec)
    
            self.write('s')
            lin = self.readline()
    
        return dev_list
    
    def write_bytes(self, hex_str):
        '''Uses the 'W' command of the HA7S to write bytes to the one-wire
        bus.  'hex_str' are the bytes to be written, expressed in HEX format,
        all caps.  The function returns all of the bytes, as a HEX string, read
        from the bus up to but not including the terminating <CR>.
        '''
        # Determine the length of the string to be written, expressed
        # in HEX, two digits, without leading 0x.
        byte_len = hex(len(hex_str)/2)[2:].upper()
        if len(byte_len)==1:
            byte_len = '0' + byte_len
        
        self.write('W%s%s\r' % (byte_len, hex_str))
        return self.readline()


class HA7Sreader(base_reader.Reader):
    """Class that reads the sensors on a 1-wire bus with a HA7S master.
    The read() method performs the read action.
    """
    
    def __init__(self, settings=None):
        """'settings' is the general settings file for the application.
        """
        # Call constructor of base class
        super(HA7Sreader, self).__init__(settings)

        # At the moment, only one device connects to the logger through
        # a TTL FTDI converter
        try:
            self.port_path = glob.glob('/dev/serial/by-id/usb-FTDI_TTL232R*')[0]
        except:
            self.port_path = None


    regex_temp = re.compile('^[0-9A-F]{18}$')
    def readTemp(self, port, addr):
        '''Returns the temperature in Fahrenheit read from the Dallas
        DS18B20 with the 16 hex digit ROM code of 'addr'.  'port' is an open
        HA7_port port.
        **Note: this command assumes the Temperature Convert command, 0x44h
        has already been issued and completed.
        '''
        port.reset()
        port.write_bytes('55%sBE' % addr)
        ret = port.write_bytes('FF' * 9)   # read entire Scratchpad in order to enable CRC check

        # Make sure return value from device is valid.
        if HA7Sreader.regex_temp.search(ret):
            # Ensure CRC is OK
            if not crc8_is_OK(ret):
                raise Exception('Bad CRC calculating temperature for %s. Return bytes were: %s' % (addr, ret))

            sign = ret[2]   # the sign HEX digit
            val = int(ret[3] + ret[:2], 16)
            if sign=='F':
                # this is a negative temperature expressed in 
                # 12-bit twos complement
                val = val - (1<<12)   
            # vals is now 1/16ths of a degree C, so convert to F
            return 32.0 + 1.8 * val/16.0
        
        else:
            raise Exception('Bad 1-wire Temperature Return Value: %s' % ret)


    regex_io = re.compile('^[0-9A-F]{8}$')
    def readIO(self, port, addr):
        """Returns the sensed level of IO channel A on a DS2406 device.
        'port' is an open HA7_port.
        'addr' is the 16 hex digit ROM code of the DS2406, using capital 
        letters for the non-numeric hex codes.
        """
        port.reset()
        cmd = 'F5C5FF'
        port.write_bytes('55%s%s' % (addr, cmd))
        # reads Channel Info byte, another Unknown byte, + two CRC16 bytes
        ret = port.write_bytes('FF'*4)  
        if HA7Sreader.regex_io.search(ret):
            if not crc16_is_OK(cmd + ret):
                raise Exception('Bad CRC reading Input for %s. Return bytes were: %s' % (addr, ret))
            val = int(ret[:2], 16) & 4
            return 1 if val else 0
        else:
            raise Exception('Bad 1-wire DS2406 Return Value: %s' % ret)            


    def read(self):
        """Read the 1-wire sensors attached to the HA7S.
        Only certain sensor families are supported:  28 (DS18B20) and 12 (DS2406)
        Returns a list of readings. The reading list consists of
        4-tuples of the form (UNIX timestamp in seconds, reading ID string, 
        reading value, reading type which is a value from the 'base_reader' module.
        """
        
        if self.port_path:
            port = HA7_port(self.port_path)
        else:
            raise Exception('No HA7S connected.')

        try:      # for making sure port is closed

            # the reading list to return.
            readings = []

            # Use the same timestamp for all the readings
            ts = time.time()
            
            # Get list of connected devices and issue Temperature Convert command
            # for all devices if any of them are DS18B20s.
            devices = port.device_list()
            temp_device_ct = len([rec for rec in devices if rec['family']=='28'])
            if temp_device_ct > 19:
                # HA7S can only supply 35 mA
                raise Exception('Too many one-wire temperature devices on bus.')
            if temp_device_ct:
                port.reset()
                port.write_bytes('CC44')    # issues temperature convert to all temp devices
                time.sleep(1.0)             # long enough for convert to occur.
                port.flushInput()

            for rec in devices:
                try:
                    if rec['family']=='28':
                        val = self.readTemp(port, rec['addr'])
                        read_type = base_reader.VALUE
                    elif rec['family']=='12':
                        val = self.readIO(port, rec['addr'])
                        read_type = base_reader.STATE
                    readings.append( (ts, rec['id'], val, read_type) )
                except:
                    logging.exception('Error reading 1-wire sensor %s' % rec['id'])

        finally:
            port.close()

        return readings

if __name__=='__main__':
    from pprint import pprint
    reader = HA7Sreader()
    pprint(reader.read())
