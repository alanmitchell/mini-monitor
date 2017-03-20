#!/usr/bin/python
"""This script listens to an MQTT broker on the localhost.  
The script processes messages on the "readings/final/#"
topics, those messages being a set of sensor readings.  The readings
are posted to a BMON server through use of the httpPoster2 module.
"""
import sys
import os
import logging
import logging.handlers
from os.path import exists
import shutil
import httpPoster2
import paho.mqtt.client as mqtt

# Access the mini-monitor settings file
# The settings file is installed in the FAT boot partition of the Pi SD card,
# so that it can be easily configured from the PC that creates the SD card.  
# Include that directory in the Path so the settings file can be found.
sys.path.insert(0, '/boot/pi_logger')
import settings

# ----- Setup Exception/Debug Logging for the Application
# Log file for the application.  
LOG_FILE = '/var/log/mqtt_to_bmon.log'

# Use the root logger for the application.

# set the log level. Because we are setting this on the logger, it will apply
# to all handlers (unless maybe you set a specific level on a handler?).
logging.root.setLevel(settings.LOG_LEVEL)

# Set logging level and stop propagation of messages from the 'requests' module
logging.getLogger('requests').propagate = False
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# create a rotating file handler
fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=200000, backupCount=5)

# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
fh.setFormatter(formatter)

# create a handler that will print to console as well.
console_h = logging.StreamHandler()
console_h.setFormatter(formatter)

# add the handlers to the logger
logging.root.addHandler(fh)
logging.root.addHandler(console_h)

# log a restart of the app
logging.warning('mqtt_to_bmon has restarted')

# ---- Create the object that will post the readings to the HTTP server.
# First copy over the saved copy of the database, since this DB is
# created on RAM disk and is lost every reboot.
db_fname = '/var/run/postQ.sqlite'       # working, RAM disk version
db_fname_nv = '/var/local/postQ.sqlite'  # non-volatile backup
if exists(db_fname_nv):
    shutil.copyfile(db_fname_nv, db_fname)
    logging.debug('Restored Post queue.')

# try twice to create Posting queue
for i in range(2):
    try:
        poster = httpPoster2.HttpPoster(settings.POST_URL,
                                        reading_converter=httpPoster2.BMSreadConverter(settings.POST_STORE_KEY),
                                        post_q_filename=db_fname,
                                        post_time_file='/var/run/last_post_time')
        logging.debug('Created HttpPoster.')
        break
    except:
        if i==0:
            # On first pass, try deleting the Post DB as it may be corrupted
            if exists(db_fname):
                os.remove(db_fname)
        else:
            logging.exception('Error creating Posting queue: %s. Terminating application.' % db_fname)
            sys.exit(1)

# ---- Start a client that will listen for MQTT messages

# The callback for when the MQTT client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Messages on this topic are sets of readings.
    client.subscribe("readings/final/#", qos=1)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # Process message payload.  Each reading is on a separate line in the
    # payload.  The reading has 3 tab-delimited fields: 
    #   Unix timestamp  -  Sensor ID  -  Sensor value
    # Need to convert this to a list of 3-element tuples
    reads = []
    for line in msg.payload.split('\n'):
        try:
            ts, sensor_id, val = line.split('\t')
            reads.append( (int(float(ts)), sensor_id, float(val)) )
        except:
            logging.exception('Bad reading: %s' % line)
            # continue with the next reading
            continue

    # hand the readings to the HTTPposter if there are any
    if len(reads):
        poster.add_readings(reads)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect('localhost')
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_forever()
