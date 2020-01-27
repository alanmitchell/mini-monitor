"""Contains a Maxim 1-Wire Sensor Reader class that is designed to work with a DS2480B
adapter attached to USB port through an FTDI USB-to-Serial converter.  The Reader is 
currently configured to read the DS18B20 temperature sensor and the DS2406 Digital Input
sensor (used with the Analysis North Motor Sensor).  But, other 1-Wire sensors can be
added to this list by modifying the TARGET_SENSORS constant below.

Beyond the Python module dependencies that are listed in the main requirements.txt
file, this module depends on the following installations:

sudo apt install owserver python3-ow

"""
import ow
import psutil
import subprocess
from pathlib import Path
import time
import serial
from . import base_reader

# Dictionary below determines which 1-Wire Sensor Families are targeted
# by this reader module, the attributes from those sensors that constitute the
# readings, and the type of reading.
# Keys are the Sensor type (e.g. DS18B20, DS2406), and the tuple items are the attribute
# to read for the sensor, its reading type, and the optional function to apply to the value.
# If there is no function to apply, use None for the third element.
TARGET_SENSORS = {
    'DS18B20': ('temperature10', base_reader.VALUE, lambda x: x * 1.8 + 32.0),
    'DS2406': ('sensed_A', base_reader.STATE, None)
}

def port_has_1wire_adapter(portstr):
    """Checks to see if there is a USB-DS2480B 1-Wire Adapter installed on the
    'portstr' port (e.g. /dev/ttyUSB0).  Returns True if so, False otherwise.
    """
    try:
        p = serial.Serial(str(portstr), timeout=0.5)
        p.reset_input_buffer()
        p.write(b'\xE3\xC1')        # Go to Command mode and issue Reset
        val = p.read(1)
        return val in (b'\xcd', b'\xed') # This is what is returned by C1 Reset command
    except:
        return False

def owserver_running():
    """Returns True if the process owserver is running, False otherwise.
    """
    for proc in psutil.process_iter():
        if 'owserver' in proc.name():
            return True
    return False


class OneWire(base_reader.Reader):
    
    def __init__(self, settings=None):
        
        # Call constructor of base class
        super(OneWire, self).__init__(settings)
        
        # Tracks the port that the 1-wire interface is on
        self.known_port = ''
        
        # start owserver
        self.start_server_if_needed()

    def start_server_if_needed(self):
        """Checks to see if the owserver is running and starts it if not.  Needs to find
        the serial port that has the 1-wire adapter attached to it.
        Returns True if the server is already running or successfully started.  Returns
        False if it can't start the server due to not finding an adapter.
        """
        # Number of seconds required for owserver to start up.
        SECONDS_FOR_STARTUP = 4.0
        
        if not owserver_running():

            if len(self.known_port):
                # has been started before using port self.known_port 
                if port_has_1wire_adapter(self.known_port):
                    subprocess.run(["/usr/bin/owserver", "-d", self.known_port])
                    time.sleep(SECONDS_FOR_STARTUP)  # give server time to start
                    return True
                else:
                    return False
                    
            else:
                # Find the port that has the adapter.  The adapter uses an FTDI
                # USB-to-Serial chip, so only search those ports.
                for p_path in base_reader.Reader.available_ftdi_ports:
                    if port_has_1wire_adapter(p_path):
                        # Save the port in case we need to restart the server later.
                        self.known_port = p_path
                        
                        # Remove this port from the Master list so other readers
                        # don't try to use it.
                        base_reader.Reader.available_ftdi_ports.remove(p_path)
                        
                        subprocess.run(["/usr/bin/owserver", "-d", p_path])
                        time.sleep(SECONDS_FOR_STARTUP)  # give server time to start
                        return True

                return False

        else:
            return True

    def read(self):
        
        # Check to see if the one-wire server is running.  If not, start it.
        if not self.start_server_if_needed():
            # no owserver, so no readings
            return []
        
        ts = int(time.time())   # same timestamp used for all readings
        readings = []
        
        # loop across all sensors, reading the ones that appear in the target
        # list defined above.
        ow.init('localhost:4304')
        for sensor in ow.Sensor('/').sensorList():
            if sensor.type in TARGET_SENSORS:
                attr, rd_type, conv_func = TARGET_SENSORS[sensor.type]
                sensor.useCache(False)
                val = float(getattr(sensor, attr))
                if conv_func:
                    val = conv_func(val)
                readings.append((ts, f'{sensor.family}.{sensor.id}', val, rd_type))
        
        return readings
