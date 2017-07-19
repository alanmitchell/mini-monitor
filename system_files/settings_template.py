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
# to connect to the Internet.
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
CELL_MODEM_MODEL = 'E173'

# ----------------------------------------------------

# Set following to True to enable posting to a BMON server
ENABLE_BMON_POST = True

# BMON URL to post readings to, and required storage key
# An example BMON URL is "https://bms.ahfc.us"
# The Store Key must match the Store Key in the settings file for
# the BMON server.
POST_URL = '[BMON URL goes here]/readingdb/reading/store/'
POST_STORE_KEY = 'Store Key Goes Here'

# A list of Sensor Reader classes goes here.
# Comment out any Sensor Readers that are not being used.
READERS = [
#'ha7s.HA7Sreader',                # 1-Wire Sensors
#'sage_boiler.Sage21Reader',      # Burnham Alpine Boilers w/ Sage 2.1 controller
#'aerco_boiler.BMS2reader',       # AERCO BMS II Boiler Mangager
#'dg700.DG700reader',             # Energy Conservatory DG-700 Pressure Gauge
#'labjack.LabjackTempReader',     # Thermistors connected to Labjack U3
#'sensaphone.SensaphoneReader',   # Reads Node sensors from Sensaphone IMS 4000
'sys_info.SysInfo',               # System uptime, CPU temperature, software version
]

# -------- Flags and Variables that control application health checks

# These default values are appropriate for a system that is on a clock
# timer that forces a power-cycle every so often.

# Number of days of uptime between forced reboots.  Set to 0 to never reboot.
REBOOT_DAYS = 0

# Reboots if Error Count is too high
CHECK_ERROR_CT = False

# Reboots if Last Post was too long ago
CHECK_LAST_POST = False

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

# --- Utility Meter Reader script

# Set to True to enable the meter reader
ENABLE_METER_READER = False

# A Python list of the Meter IDs you wish to capture and post.
METER_IDS = [1234, 6523, 1894]

# The minimum number of minutes between postings. If you set
# this too low, the resolution of the posted meter reading delta
# will be low.
METER_POST_INTERVAL = 30  # minutes

# --- Pulse Counter script ---
# See pi-energy-sensors GitHub project

# Interval between logging events in seconds
PULSE_LOG_INTERVAL = 10 * 60    # seconds

# Determines whether both edges of the pulse are counted
# or just the falling edge.
PULSE_BOTH_EDGES = False

# --- BTU Meter script ----
# See pi-energy-sensors GitHub project

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
