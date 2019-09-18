#!/usr/bin/env python3
"""Module used with classes to read the DG-700 pressure gauge.
Use the DG700reader class.
"""
   # do floating point div even with integers
import time
import serial
from . import base_reader


def open_DG():
    """Opens the DG-700 on a serial port served by a FTDI USB-to-Serial converter
    chip.  Returns the pySerial port object.
    """

    # find the device file for the FTDI RS-232 converter and open
    # a serial port.
    ser_port_path = base_reader.Reader.available_ftdi_ports[0]

    # getting 2 pressures can take 2.25 sec if auto-zero is enabled, so
    # set an appropriate timeout.
    return serial.Serial(ser_port_path, timeout=2.25)   # defaults to 9600,8,N,1


def dg700cmd(dg_port, cmd, retLen):
    '''
    Issues a command to the DG700 and returns the result.  Tests for the correct
    number of return bytes and tests for an accurate echo of the command.
    dg_port: an open pySerial port object connected to the DG-700
    cmd: a list containing the command byte value and the any needed data 
         values, or an integer for a command that needs no data.
    retLen: the number of bytes the DG700 should return, not counting echo.
    Returns the return value from the command as a list of bytes.
    Raises an error if an error in the return from the DG occurs.
    '''

    # if the command is not a list, convert to a one-element list.
    if not hasattr(cmd, '__iter__'):
        cmd = [cmd]
    
    cmdLen = len(cmd)
    
    dg_port.flushInput()
    dg_port.write(bytearray(cmd))
    ret = list(bytearray(dg_port.read(cmdLen + retLen)))
    
    # test return length first
    if len(ret) < cmdLen + retLen:
        raise ValueError('DG-700 returned too few bytes.')
    
    # test echo bytes
    for i in range(cmdLen):
        if ret[i] != ((cmd[i] + 1) % 256):
            raise ValueError('Echo bytes from DG-700 were incorrect.')
    
    return ret[cmdLen:]


def bytes_to_pascals(dg_bytes):
    """Takes a list of 3 bytes read from the DG-700 and returns a pressure
    in Pascals.
    Larry Palmiter originally wrote this code for TEC in Basic, 
    which has proven immensely useful.
    """
    bx, hi, lo = dg_bytes    # unpack the array into individual values
    pressure = 0.0
    if bx == 0:
        pressure = 0.0
    else:
        x = bx - 129
        if hi > 127:
            pressure = (-1.) * 2.**x * (1 + (256 * (hi - 128) + lo) / 2.**15)
        else:
            pressure = 2.**x * (1 + (256 * hi + lo) / 2.**15)
    return pressure


class DG700reader(base_reader.Reader):
    """Class to read pressure values from the DG-700.
    """

    def __init__(self, settings=None):
        """Initialize the DG-700.
        """
        # Call constructor of base class
        super(DG700reader, self).__init__(settings)

        # open the DG-700 serial port
        ser_port = open_DG()
        
        try:
            # disable auto-zero
            dg700cmd(ser_port, 9, 0)
            time.sleep(1.25)   # a delay after this command is required.

        except:
            raise   # re-raise the error.

        finally:
            ser_port.close()

    def read(self):
        """Read values from the DG-700 and return as a list.
        """
        
        # open the DG
        ser_port = open_DG()

        # wrap the code below in a try clause so that serial port will be explicitly
        # closed in the finally clause in the case of an error.
        try:
            # disable auto-zero
            dg700cmd(ser_port, 9, 0)
            time.sleep(1.25)   # a delay after this command is required.

            # read the two pressure values
            vals = dg700cmd(ser_port, 3, 6)
            ch1_pascals = bytes_to_pascals(vals[:3])
            ch2_pascals = bytes_to_pascals(vals[3:])

        except:
            raise        # re-raise the error

        finally:
            ser_port.close()

        ts = time.time()

        return [ (ts, '%s_dg_ch1' % self._settings.LOGGER_ID, ch1_pascals, base_reader.VALUE),
                 (ts, '%s_dg_ch2' % self._settings.LOGGER_ID, ch2_pascals, base_reader.VALUE)]

if __name__=='__main__':
    from pprint import pprint    
    rdr = DG700reader()
    pprint(rdr.read())
