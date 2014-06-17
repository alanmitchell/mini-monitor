"""Periodically requests readings from an object and then logs them
to handler at specified intervals.
"""
import logging, time
import numpy as np
import readers.base_reader

class LoggerController:

    def __init__(self, read_interval=5, log_interval=600):
        """Constructs the PeriodicReader object:
        'read_interval': the time interval between calls to the 'reader'
            read() method in seconds.
        'log_interval': the time interval between points when the readings
            are summarized and logged to the logging handlers in seconds.
        """

        self.read_interval = read_interval
        self.log_interval = log_interval

        # create a list of reader objects that read sensors.
        self.readers = []

        # create a list of handlers to be called with summarized readings
        # at each logging event.
        self.logging_handlers = []
        
        # create a dictionary to hold all the readings collected during a 
        # logging interval.  The keys of the dictionary will be the reading ID,
        # and the values will be a two-tuple, the first value being the 
        # reading_type from the readers.base_reader module, and the second value 
        # will be a list of readings, each reading being a tuple of the form:
        # (timestamp, value)
        self.read_data = {}


    def add_reader(self, reader):
        """Adds an object to the list of sensor readers.  Each reader object must have a 
        read() method that returns a list of readings. Each item in the list must be a 
        4-tuple of the form (timestamp, reading_id, reading_value, reading_type).  'timestamp'
        is a UNIX timestamp (seconds), 'reading_id' is a unique string sensor/reading id, 
        'value' is the reading value, and 'reading_type' is a constant indicating 
        the general class of reading (e.g. value, state, counter) from the 
        'readers.base_reader' module.
        """
        self.readers.append(reader)


    def add_logging_handler(self, handler):
        """Adds a handler that will be delivered summarized readings at each
        logging event.  Each handler must have an add_readings(readings) method,
        which will be passed a list of readings; each reading is a tuple
        of the form: (UNIX timestamp, sensor ID, summarized reading value): 
        """
        self.logging_handlers.append(handler)


    def log_readings(self):
        """Summarizes readings for one logging interval and passes the
        summarized values to each logging handler.  Timestamps are converted
        to integers.
        """
        
        # summarize the readings
        summarized_readings = []
        new_read_data = {}   # the new reading data structure for next interval
        for reading_id, data in self.read_data.items():
            reading_type, reading_list = data
            if len(reading_list):
                
                try:
                    logging.debug('%s: %d readings' % (reading_id, len(reading_list)))
                    # make a separate numpy array of values and time stamps
                    rd_arr = np.array(reading_list)
                    ts_arr = rd_arr[:, 0]   # first column
                    val_arr = rd_arr[:, 1]  # second column
                    
                    if reading_type == readers.base_reader.VALUE:
                        # calculate the average value to log
                        val_avg = val_arr.mean()
                        # limit this value to 5 significant figures
                        val_avg = float('%.5g' % val_avg)
                        # calculate the average timestamp to log and convert to
                        # integer seconds
                        ts_avg = int(ts_arr.mean())
                        summarized_readings.append( (ts_avg, reading_id, val_avg) )
                        
                    elif reading_type == readers.base_reader.STATE:
                        # create a summarized reading for every state change, and 
                        # also for the last reading even if it is not a state
                        # change.
                        last_state = val_arr[0]
                        ts_of_last_reading = ts_arr[-1]
                        for ts, val in reading_list[1:]:
                            if (val != last_state) or (ts==ts_of_last_reading):
                                summarized_readings.append( (int(ts), reading_id, val) )
                                last_state = val
                        # need to save the last state for the next logging interval
                        # so that the first state change can be detected.
                        new_read_data[reading_id] = (readers.base_reader.STATE, [reading_list[-1]])
                        
                    elif reading_type == readers.base_reader.COUNTER:
                        # with counter type readings, just take the last reading
                        # in the logging interval.
                        ts, val = reading_list[-1]
                        summarized_readings.append( (int(ts), reading_id, val) )
                        
                except:
                    logging.exception('Error summarizing readings for logging.')

        # Reset the reading data structure. The 'new_read_data' includes the 
        # last readings from the STATE type sensors.
        self.read_data = new_read_data
        
        # Pass summarized readings to all of the logging handlers, if there
        # are any summarized readings
        if len(summarized_readings):
            for handler in self.logging_handlers:
                try:
                    handler.add_readings(summarized_readings)
                except:
                    logging.exception('Error handling logged readings in %s' % handler)
                

    def run(self):
        """Called to starting the reading and logging process.  Infinite loop 
        and does not return.
        """

        # determine the time at which readings should be read and logged.
        next_read_time = time.time()     # read right away
        next_log_time = time.time() + self.log_interval
        

        while True:

            # check to see if it's time to log readings.
            if time.time() > next_log_time:
                next_log_time += self.log_interval
                # when the clock is being sped up by ntpd, the new log time
                # may be prior to the current time. If so, adjust it.
                if next_log_time < time.time():
                    next_log_time = time.time() + self.log_interval
                try:
                    self.log_readings()
                except:
                    logging.exception('Error logging readings.')

            # calculate the next time a set of readings should be taken. If for
            # some reason clock changed and moved forward substantially, get j
            # resynched with it.
            next_read_time = max(next_read_time + self.read_interval, time.time())

            # Loop the through the readers, adding each reading returned to 
            # the reading_data structure.
            for reader in self.readers:
                try:
                    for ts, reading_id, reading_val, reading_type in reader.read():
                        # get the entry in the reading data structure for this sensor
                        old_rd_type, rd_list = self.read_data.get(reading_id, (None, []))
                        rd_list.append( (ts, reading_val) )
                        self.read_data[reading_id] = (reading_type, rd_list)
                except:
                    logging.exception('Error processing readings from %s' % reader)
                    
            # wait until the next reading time
            while time.time() < next_read_time:
                time.sleep(0.2)
                