"""Periodically requests readings from reader objects and then posts summarized
sets of the readings to an MQTT broker on localhost.
"""
import logging, time
import os
import numpy as np
import readers.base_reader
import readers.usb_temp1
import mqtt_poster

class LoggerController:

    def __init__(self, read_interval=5, log_interval=600, logger_id='test'):
        """Constructs the PeriodicReader object:
        'read_interval': the time interval between calls to the 'reader'
            read() method in seconds.
        'log_interval': the time interval between points when the readings
            are summarized and logged to the logging handlers in seconds.
        'logger_id': the ID of this logger from the settings file.
        """

        self.read_interval = read_interval
        self.log_interval = log_interval
        self.logger_id = logger_id

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

        # Create a poster object to post readings to the local MQTT broker.
        # It runs in a separate thread and must be started
        self.poster = mqtt_poster.MQTTposter()
        self.poster.start()

        # track whether a call has been make to log readings before.
        self.first_log_call = True

        # Create the object that reads temperature from the attached USB
        # temperature sensor.
        self.temp_reader = readers.usb_temp1.USBtemperature1()


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

    def log_readings(self):
        """Summarizes readings for one logging interval and posts them to
        the MQTT broker. Timestamps are converted to integers.
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
                        ts_avg = round(ts_arr.mean(), 2)
                        summarized_readings.append( (ts_avg, reading_id, val_avg) )
                        
                    elif reading_type == readers.base_reader.STATE:
                        # create a summarized reading for every state change, and 
                        # also for the last reading even if it is not a state
                        # change.  If this is the first logging event after reboot,
                        # then also record the first reading

                        # make list of the timestamps of the special readings to record (always the
                        # last reading, and the first reading if a reboot just occurred.
                        special_ts = [ts_arr[-1]]    # last reading
                        if self.first_log_call:
                            # on first logging call, record the initial reading also
                            special_ts.append(ts_arr[0])

                        last_state = val_arr[0]
                        for ts, val in reading_list:
                            if (val != last_state) or (ts in special_ts):
                                summarized_readings.append( (round(ts, 2), reading_id, val) )
                                last_state = val
                        # need to save the last state for the next logging interval
                        # so that the first state change can be detected.
                        new_read_data[reading_id] = (readers.base_reader.STATE, [reading_list[-1]])
                        
                    elif reading_type == readers.base_reader.COUNTER:
                        # with counter type readings, just take the last reading
                        # in the logging interval.
                        ts, val = reading_list[-1]
                        summarized_readings.append( (round(ts, 2), reading_id, val) )
                        
                except:
                    logging.exception('Error summarizing readings for logging.')

        # Reset the reading data structure. The 'new_read_data' includes the 
        # last readings from the STATE type sensors.
        self.read_data = new_read_data

        self.first_log_call = False   # a call has now been made to this routine
        
        # Post summarized readings to the MQTT broker, if there
        # are any summarized readings
        if len(summarized_readings):
            # convert readings into a string, one reading per line with
            # tab-delimited fields
            post_str = '\n'.join([ '%s\t%s\t%s' % (ts, sensor_id, val) for ts, sensor_id, val in summarized_readings])
            try:
                self.poster.publish('readings/final/pi_logger', post_str)
            except:
                logging.exception('Error posting readings to MQTT broker.')

    def run(self):
        """Called for starting the reading and logging process.  Infinite loop 
        and does not return.
        """

        # determine the time at which readings should be read and logged.
        next_read_time = cur_time = time.time()     # read right away
        # Synchronize the log time with the top of the hour if the logging
        # interval is evenly divisible in to 60 minutes.
        next_log_time = cur_time - (cur_time % self.log_interval) + self.log_interval

        while True:

            # check to see if it's time to log readings.
            if time.time() > next_log_time:

                # Log the gas and temperature readings for Marco's project, giving
                # them a timestamp of exactly the log time, so that timestamps are
                # synchronized with the top of the hour.
                readings = []
                
                # Get the latest gas meter reading, if available
                gas_file = '/var/run/last_gas'
                if os.path.exists(gas_file):
                    # Only post gas reading if it is newer than 5.5 minutes
                    if time.time() - os.path.getmtime(gas_file) < 5.5 * 60:
                        try:
                            gas_val = float(open(gas_file).read())
                            readings.append((next_log_time, '%s_gas' % self.logger_id, gas_val))
                        except:
                            # File is not present or error occurred. Do not include
                            # the gas reading.
                            logging.exception('Error reading Gas Meter reading.')
                            pass

                # Get the temperature reading
                try:
                    _, _, temp_val, _ = self.temp_reader.read()[0]
                    readings.append((next_log_time, '%s_temperature' % self.logger_id, temp_val))

                    # Log Temperature Readings if logging level is DEBUG
                    if logging.root.getEffectiveLevel() == logging.DEBUG:
                        with open('/home/pi/temp.txt', 'a') as log_file:
                            log_file.write('%s\t%s\n' % (next_log_time, temp_val))

                except:
                    logging.exception('Error reading Temperature.')
                    pass

                if len(readings):
                    # convert readings into a string, one reading per line with
                    # tab-delimited fields
                    post_str = '\n'.join([ '%s\t%s\t%s' % (ts, sensor_id, val) for ts, sensor_id, val in readings])
                    try:
                        self.poster.publish('readings/final/pi_logger', post_str)
                    except:
                        logging.exception('Error posting readings to MQTT broker.')

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
                time.sleep(0.1)
                