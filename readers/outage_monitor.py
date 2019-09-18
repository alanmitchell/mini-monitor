#!/usr/bin/env python3
"""Reader module for detecting a  power outage as indicated by the state of
a Raspberry Pi digital I/O pin:  1 power is present, 0 is power is absent.
"""
import time
from . import base_reader
import RPi.GPIO as GPIO

# BCM pin number of the Raspberry Pi pin used to read current state
# of power.
PIN_STATE = 16

class OutageMonitor(base_reader.Reader):

    def read(self):

        # Set up digital I/O pin that reads the state of the power.
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_STATE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Use the ID of this logger to create a unique ID.
        sensor_id = '%s_state' % (self._settings.LOGGER_ID)

        # Timestamp of current state
        ts = time.time()

        readings = [(ts, sensor_id, GPIO.input(PIN_STATE), base_reader.STATE)]

        return readings


if __name__ == '__main__':
    # This script can be run directly for testing.
    from pprint import pprint

    rdr = OutageMonitor()
    pprint(rdr.read())