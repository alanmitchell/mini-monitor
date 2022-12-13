"""Holds the user modifiable settings for the application.
"""
import logging

# The unique ID of this particular logger, which will be prepended to
# sensor IDs.
LOGGER_ID = 'test'

# The intervals for reading sensors and for logging readings
READ_INTERVAL = 5   # seconds between readings
LOG_INTERVAL = 10*60  # seconds between logging data

# ----------- Cellular Modem Related -------------
# Set following to True if you are using a USB Cellular modem
# to connect to the Internet, **except** that some types of
# modems such as the ZTE MF197 appear as an Ethernet port on the
# Pi.  With these modems, leave the "USE_CELL_MODEM" parameter 
# set to  False.
USE_CELL_MODEM = False

# If you are using a cell modem, set the following to a string indicating
# the type of cell modem you are using.  This string must be one of the
# "Dialer" sections in the wvdial.conf file found in the /boot/pi_logger
# folder (the folder also containing the Mini-Monitor settings file.)
# Currently, the following value are supported:
#
#     E173: Works with the Huawei E173 mdoem
#     E3276: Works with the Huawei E3276 modem
#     E1756C: Works with the Huawei E1756C modem
#     MF197: Works with the ZTE MF197 modem when operating in serial mode
#        Note that this modem sometimes ships with firmware that makes it
#        appear as a USB-to-Ethernet converter.  For that firmware, set
#        USE_CELL_MODEM to False.
#
# Mini-Monitor uses the WvDial Linux utility to connect the cell modem
# to the Internet.  The /boot/pi_logger/wvdial.conf is the configuration
# file for WvDial and can be edited to modify configuration settings and/or
# enter new Dialer sections to support different models of modems.  Also,
# The wvdial.conf file is set up with the APN of the GCI carrier in Alaska.
# (see the Init3 configuration settings). This can be modified for other carriers.
# See documentation of the Linux WvDial program for further information on
# the configuration file.
# NOTE: some versions of the E1756C modem did not reliably connect using
# the current wvdial.conf settings.  Use the E173 or E3276 modems if possible.
# *** This value must be in single or double quotes ***
CELL_MODEM_MODEL = 'E173'

# ----------------------------------------------------
# Blues Wireless Notecard server settings. Mini-monitor can post readings
# through a Blues Wireless Notecard.  The settings below control startup of
# the server and import configuration.

# Set to True to start Notecard server
ENABlE_NOTECARD = False

# The project ID on the Notehub
NOTECARD_PRODUCT = 'us.ahfc.tboyes:sensor_readings'

# A string that identifies this Notecard and Pi
NOTECARD_SN_STRING = 'ID String'

# A comma-separated list of destinations for the sensor readings. These will be 
# used to route the data the Blues Notehub to BMON systems or other servers that
# can accept the data.
NOTECARD_DESTINATIONS = 'ahfc_bmon'

# *** IMPORTANT NOTE *** You must set the POST_URL setting in the next section 
# to "http://localcost:5000/minimon" to use the Notecard server.  The POST_STORE_KEY
# setting is irrelevant and can be set to anything.


# ----------------------------------------------------

# Set following to True to enable posting to a BMON server
ENABLE_BMON_POST = True

# BMON URL to post readings to, and required storage key
# An example BMON URL is "https://bms.ahfc.us"
# The Store Key must match the Store Key in the settings file for
# the BMON server.
# NOTE: if using the Blues Notecard to transmit data, complete settings in the section
# above, and set POST_URL to "http://localhost:5000/minimon"
POST_URL = '[BMON URL goes here]/readingdb/reading/store/'
POST_STORE_KEY = 'Store Key Goes Here'

# A list of Sensor Reader classes goes here.
# Comment out any Sensor Readers that are not being used.
READERS = [
#'onewire.OneWire',               # 1-Wire Sensors using USB-to-DS2480B Adapter
#'sage_boiler.Sage21Reader',      # Burnham Alpine Boilers w/ Sage 2.1 controller
#'aerco_boiler.BMS2reader',       # AERCO BMS II Boiler Mangager
#'dg700.DG700reader',             # Energy Conservatory DG-700 Pressure Gauge
#'labjack.LabjackTempReader',     # Thermistors connected to Labjack U3
#'labjack_analog.LabjackAnalog',  # Reads 4 analog channels on Labjack U3
#'sensaphone.SensaphoneReader',   # Reads Node sensors from Sensaphone IMS 4000
#'outage_monitor.OutageMonitor',  # Detects Power Outages through state of GPIO pin
#'usb_temp1.USBtemperature1',      # Reads one 1-wire temperature sensor for Marco project. USB master.
#'rms_6ch.RMS_6ch',                # 6 channel RMS voltage reader
#'modbus_tcp.ModbusTCPreader',     # Reads values from Modbus TCP servers.
#'modbus_rtu.ModbusRTUreader',     # Reads values from Modbus RTU servers.
#'onicon_sys10.OniconSystem10',    # Reads BTU, flow & temperature values from an Onicon System 10 BTU meter.
'sys_info.SysInfo',              # System uptime, CPU temperature, software version
]

# -------- Flags and Variables that control application health checks

# These default values are appropriate for a system that is on a clock
# timer that forces a power-cycle every so often.

# Number of days of uptime between forced reboots.  Set to 0 to never reboot.
REBOOT_DAYS = 2

# Reboots if Error Count is too high
CHECK_ERROR_CT = False

# Reboots if Last Post was too long ago.
CHECK_LAST_POST = False

# If CHECK_LAST_POST is TRUE then a reboot will occur if the last
# post occurred more than LAST_POST_REBOOT_DELAY hours ago.
LAST_POST_REBOOT_DELAY = 4.0    # hours

# This controls what messages will actually get logged in the system log
# 'Logging' here does *not* refer to sensor logging; this is error and debug
# logging.
# Levels in order from least to greatest severity are:  DEBUG, INFO, WARNING,
# ERROR, CRITICAL
LOG_LEVEL = logging.INFO

# ---------------------------------------------------------------------------
# Below are settings that are only used for certain pi_logger Sensor Readers and
# processes producing sensor readings.

# ---- Sensaphone settings
# If you are using the sensaphone.SensaphoneReader reader, then you need
# to set the IP address of the Host Sensaphone unit below
SENSAPHONE_HOST_IP = '10.30.5.77'

# ------------ Utility Meter Reader script --------------

# Set to True to enable the meter reader
ENABLE_METER_READER = False

# A Python list of the Meter IDs you wish to capture and post.
# Use empty brackets to read all meters, i.e.:  []
METER_IDS = [1234, 6523, 1894]

# The minimum number of minutes between postings. If you set
# this too low, the resolution of the posted meter reading delta
# will be low.
METER_POST_INTERVAL = 30  # minutes

# The multipliers below are applied to the rate of change calculated from
# sequential meter readings.  They can be used to convert that
# rate of change into engineering units, such as BTU/hour.
# There is a separate multiplier for Gas Meters, Electric Meters and Water Meters.
# *** NOTE: If you set a multiplier to 0, that type of Meter (gas, electric, water)
# will not be recorded by the Mini Monitor.
METER_MULT_GAS = 1000.0       # Converts Cubic Feet/hour to Btu/hour
METER_MULT_ELEC = 1.0         # Electric Meter Multiplier
METER_MULT_WATER = 1.0        # Water Meter Multiplier

# -------- RTL-SDR 433 MHz Wireless Sensor Reader --------
# Set to True to enable this reader
ENABLE_RTL433_READER = False

# -------------------- Power Monitor Script -----------------------
# See power_monitor.py, script to read PZEM-016 electric power sensor.

# Set to True to enable the Power Monitor program
ENABLE_POWER_MONITOR = False

# Path to the Serial Port used by the RS-485 adapter
PWR_PORT = '/dev/ttyUSB0'

# Number of Wraps through the current transformer.  This will be used 
# to divide Power and Current readings.  The PZEM-016 CT is a 100 Amp CT,
#  so generally I wrap 5 turns through the CT to reduce the range to
# 0 - 20 Amps.
PWR_CT_WRAPS = 5

# Determines what values will be posted from Power Monitor
PWR_INCL_PWR_AVG = True      # Average power in interval
PWR_INCL_PWR = True          # Detailed power curve
PWR_INCL_VOLT = True         # Detailed Voltage
PWR_INCL_AMP = True          # Detailed Current
PWR_INCL_FREQ = True         # Detailed Frequency
PWR_INCL_PF = True           # Detailed Power Factor

# Change Thresholds for each of the measrement types.  These determine
# whether a new point is registered.
PWR_THRESHOLD_PWR = 3.0    # Watts, resolution is 0.1 W / PWR_CT_WRAPS
PWR_THRESHOLD_VOLT = 0.3   # Volts, resolution of sensor is 0.1 Volt
PWR_THRESHOLD_AMP = 0.03   # Amps, resolution is 0.001 A / PWR_CT_WRAPS
PWR_THRESHOLD_FREQ = 0.1   # Hz, resolution of sensor is 0.1 Hz
PWR_THRESHOLD_PF = 0.02    # Power factor, resolution is 0.01

# Maximum number of reads of the sensor before a new point will be 
# recorded, even if sufficient change has not occurred.  Reads of 
# the sensor occur roughly every second, so a value of 60 here means
# a reading will be posted at least every 60 seconds.
# Set this to None to allow any interval between change  values, remembering
# that the first reading of a logging interval will always be posted.
PWR_MAX_INTERVAL = 180    # seconds, approximately

# --------------- Multi-Channel Pulse Counter script ------------
# See pi-energy-sensors GitHub project for the scripts configured here.

# Enables the multi-channel pulse counter script.  The old single-channel
# counter is no longer needed, as the multi-channel can be configured to
# read one channel as well.
ENABLE_PULSE_COUNTER_MULTI_CH = False

# List the Pin numbers to count within the brackets below (Python list)
# Use BCM pin numbering to specify the pins on the Pi.
PULSE_INPUT_PINS = [16, 17]

# Interval between logging events in seconds
PULSE_LOG_INTERVAL = 10 * 60    # seconds

# Determines whether both edges of the pulse are counted
# or just the falling edge.
PULSE_BOTH_EDGES = False

# ---------------------- BTU Meter script -----------------------
# See pi-energy-sensors GitHub project for the scripts configured here.

# Set to True to enable the BTU meter script
ENABLE_BTU_METER = False

# Interval between logging events in seconds
BTU_LOG_INTERVAL = 10 * 60    # seconds

# Delta-T's (deg F) less than this will be considered to be
# a zero delta-T (no energy flow)
BTU_MIN_DELTA_T = 0.2    # deg F

# Determines whether both edges of the pulse are counted
# or just the falling edge.
BTU_BOTH_EDGES = False

# Calibration offsets to add to hot and cold temperature
# sensors.  Degrees F.
CALIBRATE_ADJ_HOT = 0.0
CALIBRATE_ADJ_COLD = 0.0

# -------------------- 6 channel RMS Voltage Reader ---------------------
# Associated reader is rms_6ch.py

# Gain setting for the ADS1015 ADC converter.  See documentation
# of ADS1015 for values and meanings.  This can be a single value
# applied to all 6 channels, or a list of 6 different values.

RMS_6CH_GAIN = 1         # +/- 4.096 V

# These multipliers are applied to the RMS voltage reading on each
# channel to convert to other units.  It can be one value applied
# to all channels, or a list of 6 separate values.
RMS_6CH_MULT = 1.0

# ------------------- Modbus TCP Server Reader -------------------------
# Associated reader: modbus_tcp.ModbusTCPreader

# The reader uses the MODBUS_TARGETS setting below.  Because the setting
# contains a lot of information, it is most clearly created by first creating
# variables holding Modbus device information and variables holding information
# about registers to read.  In the example below, those variables are:
#     device1, device1_sensors, device2, device2_sensors
# These variables are not required, are not used directly by the Reader, and are
# only present to make consutruction of the MODBUS_TARGETS setting more clear.
# The example below is explained in comments beneath the example.

device1 = ('abc.dyndns.org', 30000)
device1_sensors = (
    (2084, 'heat_rate'),
    (2086, 'total_heat', dict(datatype='uint32', reading_type='counter')),
    (2105, 'ret_temp', dict(register_type='input', transform='val/10')),
)

device2 = ('abc.dyndns.org', 30000, dict(endian='little', device_addr=2))
device2_sensors = (
    (2103, 'hsout', dict(transform='val/10')),
    (2102, 'hsin', dict(transform='val/10')),
)

MODBUS_TARGETS = (
    (device1, device1_sensors),      # a Modbus device and values that should be read
    (device2, device2_sensors),
)

# First, the structure of MODBUS_TARGETS is a tuple (or list) of tuples.  Each
# contained tuple describes one Modbus Device and the values that should be read from 
# that device.  In the example above, 'device1' describes the first Modbus device to query
# and 'device1_sensors' describes the values that should be read from that device.  
# 
# The first two elements of the 'device1' tuple are required and give the Host name or IP 
# address, and the Port.  'device1' in the example above is the minimal required description
# and only contains those two elements.
#
# There is an optional third element in the Modbus device description, which is a
# dictionary of other information about the device.  'device2' in the example above uses that
# optional dictionary to provide more information about the device.  Valid keys in that dictionary
# are:
#    endian:       Can have the values of 'big' (the default) or 'little'.  For sensor values that
#                  use more than one Modbus register (e.g. a floating point value), 'big' 
#                  endian means that the most-significant word is the first register address.
#                  'little' endian means the least-signficant word is the first address.
#    device_addr:  This is the Modbus unit or device address of the device being read.
#                  It defaults to 1, but can the value from 1 to 247.
#
# For each Modbus device to be queried, there is a list of sensors or values to be read from the
# device.  In the example above, 'device1_sensors' and 'device2_sensors' are two such lists (tuples 
# in this case).  Each item in the list a sensor or value, which is in turn described by a tuple
# of information.  The first device1 sensor is (2084, 'heat_rate').  These two pieces of information
# are the only required elments of the sensor descripiton.  2084 is the Modbus register address, and
# 'heat_rate' is the name that will be used in mini-monitor to create a sensor ID.  Mini-monitor Sensor IDs
# are created by concatenating the LOGGER_ID and this name.  If the LOGGER_ID in the settings file were
# 'test', the final Sensor ID for this sensor woudl be 'test_heat_rate'.
#
# Each sensor can also have a third optional element of description, which is dictionary.  In the example
# above, most sensors in 'device1_sensors' and 'device2_sensors' have this third dictionary element.
# The valid keys in this dictionary are:
#     datatype: The dataype of the value being read from the register(s).  Possible values are:
#               uint16:  (the default) unsigned, 16 bit integer, 1 Modbus register
#               int16:   signed 16 bit integer, 1 Modbus register
#               unint32: unsigned 32 bit integer, 2 registers
#               int32:   signed 32 bit integer, 2 registers
#               float:   32 bit floating point value, 2 registers
#               float32: same as 'float'
#               double:  64 bit floating point value, 4 registers
#               float64: same as 'double'
#               Some of these datatypes occupy multiple Modbus registers, so require the reading of 
#               multiple registers.
#     register_type: The type of Modbus register to read.  Possible values are:
#               'holding': (the default) holding register
#               'input':   input register
#               'coil':    coil register
#               'discrete': discrete input register
#     transform: Some Modbus values need to be transformed or coverted into final engineering units.
#                This dictionary item can provide a transform function for that purpose.  The raw
#                Modbus value is held in the variable named 'val', so that a transform of 'val/10'
#                means divide the Modbus value by 10.
#     reading_type: This entry tells Mini-Monitor what type of a value this reading is.  Possible
#                values are:
#                'value': (the default) a continuosly variable analog value like temperature, humidity, power.
#                'state': a discrete value that indicates the particular state or status of a device.
#                'counter': a cumulative counter value (such as total energy use, total water use, etc)
#                       that increases over time as a quantity is used or measured.

# ------------------- Modbus RTU Server Reader -------------------------
# Associated reader: modbus_rtu.ModbusRTUreader

# The settings format for this reader is very similar to the prior Modbus TCP reader.
# The configuration of the "sensors" (values) to read from the Modbus device is exactly the
# same as the prior TCP reader.  The only difference for the RTU reader is the tuple
# that describes the Modbus device to read.

# Here is an example configuration to read a PZEM-016 power sensor, with explanation below
# the examples (remove triple-quotes surrounding code block to use):

'''
rtu_device1 = ('/dev/ttyUSB0', 1, dict(endian='little'))
d1_sensors = (
    (0, 'voltage', dict(register_type='input', transform='val/10')),
    (1, 'current', dict(datatype='uint32', register_type='input', transform='val/1000')),
    (3, 'power', dict(datatype='uint32', register_type='input', transform='val/10')),
    (7, 'frequency', dict(register_type='input', transform='val/10')),
    (8, 'power_factor', dict(register_type='input', transform='val/100')),
)

# Here is the required Settings variable to use the Modbus RTU reader.  The above variables
# were just used to make a clearer presentation.
MODBUS_RTU_TARGETS = (
    (rtu_device1, d1_sensors),
)
'''

# The 'rtu_device1' variable holds the device configuration.  The first two elements of the tuple
# are required.  The first element is the Serial port used to communicate with the Modbus RTU device.
# The second required element is the Modbus address of the device, a number from 1 to 247.
# The third element of the tuple is optional, but if present is a dictionary of additional keyword
# arguments related to the device.  Possible keywords are:
#    endian:  Can have the values of 'big' (the default) or 'little'.  For sensor values that
#             use more than one Modbus register (e.g. a floating point value), 'big' 
#             endian means that the most-significant word is the first register address.
#            'little' endian means the least-signficant word is the first address.
#    timeout: The number of seconds this computer will wait for a response from the device
#             before timing out with an error.  Defaults to 1.0.
#    baudrate:  The baudrate used for the serial port, defaults to 9600.

# The sensor configuration, 'd1_sensors' in this example, is exactly as described in the Modbus
# TCP setup before.

# --------------------
# Here is a MODBUS RTU example for the Onicon System 10 BTU meter (remove triple quotes
# surrounding code block to use):

'''
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
'''

# The only critical names are "gbtu", "kbtu" and "mbtu" for this class to work.  Temperature and flow variables
# could be named differently.
