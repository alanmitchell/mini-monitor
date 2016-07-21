"""Holds the user modifiable settings for the application.
"""
import logging

# The unique ID of this particular logger, which will be prepended to
# sensor IDs.
LOGGER_ID = 'test'

# The intervals for reading sensors and for logging readings
READ_INTERVAL = 5   # seconds between readings
LOG_INTERVAL = 10*60  # seconds between logging data

# URL to post readings to, and required storage key
# An example BMON URL is "https://bms.ahfc.us"
# The Store Key can be any string with no spaces
POST_URL = '[BMON URL goes here]/readingdb/reading/store/'
POST_STORE_KEY = 'Store Key Goes Here'

# A list of sensor reader classes goes here
READERS = [
'ha7s.HA7Sreader',                # 1-Wire Sensors
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
# Below are settings that are only used for certain Sensor Readers

# If you are using the sensaphone.SensaphoneReader reader, then you need
# to set the IP address of the Host Sensaphone unit below
SENSAPHONE_HOST_IP = '10.30.5.77'
