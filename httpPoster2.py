"""Software to receive sensor readings from data sources and post
them to a HTTP URL.  Readings are cached if an Internet connection 
is not available, or the the post fails for any reason.

TO DO:
    * Test separate threads writing to post_time_file simultaneously
    * Perhaps abandon post if it isn't successful after a few retries. It would
        be left in the 'processing' queue, so would get tried again upon a 
        restart. This protects against some bad format locking up a post worker.
        But if post is abandoned and Internet comes back, it will be left in
        processing queue.
"""

import time, sys
import threading, json, logging
import requests
import sqlite_queue

class HttpPoster:
    """A class to post readings to a URL via HTTP.  The readings to be posted
    are delivered to this object via the addReadings() method.
    """
    
    def __init__(self, post_URL, 
                       reading_converter=None, 
                       post_q_filename='postQ.sqlite', 
                       post_thread_count=2, 
                       post_time_file='/var/local/last_post_time'):
        """Parameters are:
        'post_URL': URL to post the data to.
        'reading_converter': function or callable to convert the format
            of the readings delivered to the "addReadings" method, if
            required.
        'post_q_filename': name of the file to use for implementing the
            queue.
        'post_thread_count': number of post worker threads to start up.
        'post_time_file': name of the file to store the last time that
            a successful post occurred. (Unix timestamp).
        """
        
        self.reading_converter = reading_converter

        # create the queue used to store the readings.
        self.post_Q = sqlite_queue.SqliteReliableQueue(post_q_filename)
        
        # start the posting worker threads
        for i in range(post_thread_count):
            PostWorker(self.post_Q, post_URL, post_time_file).start()
            
    def add_readings(self, reading_data):
        """Adds a set of readings to the posting queue.  The 'reading_data' 
        variable will be converted to JSON and posted to the HTTP server.  So, 
        the server must understand that format.  If there is a converting
        function present, use it to convert the readings.
        """
        if self.reading_converter:
            self.post_Q.append(self.reading_converter(reading_data))
        else:
            self.post_Q.append(reading_data)


class PostWorker(threading.Thread):
    """
    A class to post readings to an HTTP server.
    Make sure the HTTP server responds with a status code of 200 if it receives
    the readings, even though those readings may be badly formatted or duplicates.
    Otherwise, this object will continue to try to repost the bad readings.
    """

    def __init__ (self, source_Q, post_URL, post_time_file):
        """ Create the posting worker in its own thread.
        'sourceQ': the ReadingQueue to get postings from.
        'postURL': the URL to post to, w/o any parameters
        'post_time_file': the name of a file to record the time of 
             a successful post.
        """  
        # run constructor of base class
        threading.Thread.__init__(self)
        
        # If only thing left running are daemon threads, Python will exit.
        self.daemon = True   
        self.source_Q = source_Q
        self.post_URL = post_URL
        self.post_time_file = post_time_file
       
        
    def run(self):
        
        while True:

            try:
                # get the next list of readings to post.  the 'q_id' identifies
                # this set of readings so it can be dropped from queue when 
                # finished.
                q_id, readings = self.source_Q.popleft()
                
                # encode these as json to put into the post
                post_data = json.dumps(readings)
            except:
                logging.exception('Error popping or JSON Encoding readings to post.')
                time.sleep(5)   # to limit rapid fire errors
                continue   # go back and pop another

            retry_delay = 15  # start with a 15 second delay before retrying a post
            while True:
                try:
                    # need to *not* verify SSL requests as Python 2.7.3 has an issue with
                    # requests SSL verification causing to fail when cert is actually OK.
                    req = requests.post(self.post_URL, data=post_data, timeout=15, verify=False)
                    if req.status_code == 200:
                        if logging.root.level == logging.DEBUG:
                            logging.debug('posted: %s, %s' % (readings, req.text))
                        else:
                            logging.info('posted %d bytes' % len(post_data))
                        
                        # tell the queue that this item is complete
                        self.source_Q.finished(q_id)
                        
                        # record the time of the post in the file ignoring
                        # errors (which might be caused by another worker writing
                        # to the file simultaneously.
                        try:
                            fout = open(self.post_time_file, 'w')
                            fout.write(str(time.time()))
                            fout.close()
                        except:
                            pass
                            
                        break   # and get another item from the queue
                        
                    else:
                        raise Exception('Bad Post Status Code: %s' % req.status_code)
                        
                except:
                    logging.exception("Error posting: %s" % readings)
                    time.sleep(retry_delay)   # try again later
                    if retry_delay < 8 * 60:
                        retry_delay *= 2

class BMSreadConverter:
    """Used to create the needed data structure for posting to the BMS application
    server.  Adds the 'storeKey' to a set of readings.
    """

    def __init__(self, store_key):
        self.store_key = store_key

    def __call__(self, readings):
        return {'storeKey': self.store_key, 'readings': readings}

