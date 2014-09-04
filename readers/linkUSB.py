#!/usr/bin/python
"""Module used to read devices on a Dallas 1-wire bus using the OWFS library
(see owfs.org).  The class the does the reading of the bus is OneWireReader.
"""
import logging, time, re
import serial
import base_reader


class LinkUSBreader(base_reader.Reader):
    """Class that reads the sensors on a 1-wire bus with a LinkUSB master.
    The read() method performs the read action.
    """
    
    def __init__(self, settings=None):
        """'settings' is the general settings file for the application.
        """
        # Call constructor of base class
        super(LinkUSBreader, self).__init__(settings)

        # find the FTDI port that connects to the LinkUSB, and then
        # remove it from the list of available FTDI ports.
        self.port_path = None
        for p_path in base_reader.Reader.available_ftdi_ports:
            try:
                port = serial.Serial(p_path, baudrate=9600, timeout=0.1)
                port.write(' ')
                if port.read(4)=='Link':
                    self.port_path = p_path
                    # remove port from the available list
                    base_reader.Reader.available_ftdi_ports.remove(p_path)
                    break

            except:
                pass

            finally:
                try:
                    port.close()
                except:
                    pass


    # device search return pattern
    regex_dev = re.compile('^([\+-]),([0-9A-F]{16})\s*$')  
    def deviceList(self, port):
        """Returns a list of devices found on the one-wire bus.
        'port' is an open pySerial port connected to a LinkUSB.
        Each item in the returned list is a dictionary with characteristics
        of the found device.
        """
        port.write('\r')   # make sure in ASCII mode
        time.sleep(.1)
        port.flushInput()
        
        # list of devices found
        dev_list = []
        # find the first device
        port.write('f')
        r = LinkUSBreader.regex_dev.search(port.readline())
        while r:
            indicator, r_addr = r.groups()
            rec = {}
            rec['family'] = r_addr[-2:]   # family code
            # unreverse the address
            rec['addr'] = ''
            for i in range(0, 16, 2):
                rec['addr'] += r_addr[14-i:14-i+2]
            # make the id in the format used by the BMS system
            rec['id'] = '%s.%s' % (rec['family'], rec['addr'][2:-2])
            dev_list.append(rec)

            # a minus sign indicates this is the last found device
            # on the bus.
            if indicator == '-':
                break

            port.write('n')
            r = LinkUSBreader.regex_dev.search(port.readline())
        
        return dev_list            

    regex_temp = re.compile('^[0-9A-F]{4}$')
    def readTemp(self, port, addr):
        """Returns the temperature in Fahrenheit read from the Dallas
        DS18B20 with the 16 hex digit ROM code of 'addr'.  'port' is an open
        pySerial port connected to a LinkUSB Master.
        **Note: this command assumes the Temperature Convert command, 0x44h
        has already been issued and completed.
        """
        port.write('\rrb55' + addr + 'BE')
        time.sleep(.1)   # appears to be critical! and does not work at 0.04 sleep
        port.flushInput()
        port.write('FFFF')
        lsb_msb = port.read(4)
        port.write('\r')    # back to ASCII mode
        
        # Make sure return value from device is valid.  Don't allow 'FFFF'
        # which is actually a valid return, but it also occurs when no 
        # device responds to the read request.
        if lsb_msb!='FFFF' and LinkUSBreader.regex_temp.search(lsb_msb):
            sign = lsb_msb[2]   # the sign HEX digit
            val = int(lsb_msb[3] + lsb_msb[:2], 16)
            if sign=='F':
                # this is a negative temperature expressed in 
                # 12-bit twos complement
                val = val - (1<<12)   
            # vals is now 1/16ths of a degree C, so convert to F
            return 32.0 + 1.8 * val/16.0
        
        else:
            raise Exception('Bad 1-wire Temperature Return Value: %s' % lsb_msb)


    regex_io = re.compile('^[0-9A-F]{2}$')
    def readIO(self, port, addr):
        """Returns the sensed level of IO channel A on a DS2406 device.
        'port' is an open pySerial port connected to a LinkUSB.
        'addr' is the 16 hex digit ROM code of the DS2406, using capital 
        letters for the non-numeric hex codes.
        """
        port.write('\rrb55' + addr + 'F5C4FF')
        time.sleep(.1)
        port.flushInput()
        port.write('FF')
        val = port.read(2)
        port.write('\r')
        # Return of 'FF' indicates bad address or no response.
        if val!='FF' and LinkUSBreader.regex_io.search(val):
            val = int(val, 16) & 4
            return 1 if val else 0
        else:
            raise Exception('Bad 1-wire DS2406 Return Value: %s' % val)            

    def read(self):
        """Read the 1-wire sensors attached to the LinkUSB.
        Returns a list of readings. The reading list consists of
        4-tuples of the form (UNIX timestamp in seconds, reading ID string, 
        reading value, reading type which is a value from the 'base_reader' module.
        """
        
        if self.port_path:
            port = serial.Serial(self.port_path, baudrate=9600, timeout=0.1)
        else:
            raise Exception('No LinkUSB connected.')

        # the reading list to return.
        readings = []

        # Use the same timestamp for all the readings
        ts = time.time()
        
        # Get list of connected devices and issue Temperature Convert command
        # for all devices if any of them are DS18B20s.
        devices = self.deviceList(port)
        if '28' in [rec['family'] for rec in devices]:
            port.write('\rrbCC\rp44')  # issues strong-pull-up after convert command
            time.sleep(1.0)   # long enough for convert to occur.

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

        port.close()
        
        return readings

if __name__=='__main__':
    from pprint import pprint
    reader = LinkUSBreader()
    pprint(reader.read())