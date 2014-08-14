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
#POST_URL = 'http://192.168.1.43:8000/readingdb/reading/store/'
#POST_STORE_KEY = 'PutStorageKeyHere'
POST_URL = 'http://bms.ahfconline.net/readingdb/reading/store/'
POST_STORE_KEY = 'x7sGrAWjcgZW'

# A list of sensor reader classes goes here
READERS = [
#'sage_boiler.Sage21Reader',
#'aerco_boiler.BMS2reader',
#'dg700.DG700reader',
#'labjack.LabjackTempReader',
'onewire.OneWireReader',
'sys_info.SysInfo',
]

# This controls what messages will actually get logged in the system log
# 'Logging' here does *not* refer to sensor logging; this is error and debug
# logging.
# Levels in order from least to greatest severity are:  DEBUG, INFO, WARNING, 
# ERROR, CRITICAL
LOG_LEVEL = logging.INFO

# If True, log files will be uploaded to analysisnorth.com at boot up.
# See /pi_logger/scripts/upload_logs.py for details.
UPLOAD_LOGS = True
