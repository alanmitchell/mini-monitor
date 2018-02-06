"""Has a class that listens for raw readings from the MQTT broker, and
stores and allows retrieval of the most current reading for each sensor.
"""
import logging
import threading
import paho.mqtt.client as mqtt

class MQTTcurrentReading(threading.Thread):

    def __init__(self):
        # Establish a dictionary for the for the most current readings to be
        # stored in.
        self._readings = {}

    def run(self):

        # ---- Start a client that will listen for MQTT messages

        # The callback for when the MQTT client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            # Messages on this topic are sets of readings.
            client.subscribe("readings/raw/#", qos=1)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            # Process message payload.  Each reading is on a separate line in the
            # payload.  The reading has 3 tab-delimited fields:
            #   Unix timestamp  -  Sensor ID  -  Sensor value
            # Need to convert this to a list of 3-element tuples
            reads = []
            for line in msg.payload.split('\n'):
                if len(line.strip())==0:
                    # skip blank lines
                    continue
                try:
                    ts, sensor_id, val = line.split('\t')
                    val = (float(ts), float(val))
                    self._readings[sensor_id] = val
                except:
                    logging.exception('Bad reading: %s' % line)
                    # continue with the next reading
                    continue

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect('localhost')

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        client.loop_forever()

    def get_current_reading(self, sensor_id):
        return self._readings.get(sensor_id, (None, None))
