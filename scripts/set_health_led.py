#!/usr/bin/env python3
"""Script to do basic health checks of the system and turn on an LED on
BCM pin 12 (pin 32 on header) if they pass, turn Off otherwise.
"""

import time
import RPi.GPIO as GPIO
import subprocess

# The BCM pin number that the LED is wired to.  When the pin
# is at 3.3V the LED is On.
LED_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)

# ----- Test for Internet availability.

# Try to ping for a minute before declaring that the Internet
# is not available
internet_available = False
for i in range(12):
    if subprocess.call('/bin/ping -q -c1 8.8.8.8', shell=True) == 0:
        internet_available = True
        break
    time.sleep(5)

# Set LED according to results of test
GPIO.output(LED_PIN, internet_available)
