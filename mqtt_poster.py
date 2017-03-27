import threading
import time
import Queue
import socket
import paho.mqtt.publish as publish

class MQTTposter(threading.Thread):
    """Class that runs in a separate thread and publishes to an MQTT broker.
    I found that this approach will reliably get messages to the broker in cases where
    the broker is intermittently available.  Using the 'loop_start()' method on a Client
    object doesn't seem to deliver the messages that were published while the broker was
    unavailable.
    """

    def __init__(self, host='localhost', port=1883):
        """'host' is the hostname to publish to.
        'port' is the port on the host to publish to."""
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.q = Queue.Queue()

    def run(self):
        """Processes (publishes) any items in the Queue.
        """
        while True:
            try:
                topic, payload = self.q.get(block=True)   # block until item is available
            except:
                # bad item format
                continue

            retry_wait = 1  # seconds
            while True:    # try to publish until successful
                try:
                    publish.single(topic, payload=payload, qos=1, hostname=self.host, port=self.port)
                except socket.error:
                    # couldn't connect to MQTT broker, try again after short wait
                    time.sleep(retry_wait)
                    retry_wait = min(30, retry_wait * 2)
                    continue
                except:
                    # some other error occurred. Ignore this message and go on to next
                    break
                # successfully published, so go on to next item.
                break
        
    def publish(self, topic, payload):
        """Put a message in the queue to publish.
        'topic' is the topic of the message and 'payload' is the payload.
        """
        self.q.put((topic, payload))
