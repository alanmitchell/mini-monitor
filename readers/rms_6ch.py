"""Reader module for reading 6 channels of RMS voltage from a pair of
Adafruit ADS1015 ADC breakout boards.

Values in the Settings files related to this reader:

RMS_6CH_GAIN:  This can be a list of 6 values, one for each channel
    or one value, which will then apply to all channels.  The value(s) are
    the gain settings for the ADS1015 ADC converter.  Possible values are
    2/3, 1, 2, 4, 8, 16.  See the ADS1015 datasheet for the voltage ranges
    supported by those gain values.  If this setting is not present in the
    Settings file, the gain defaults to 1.
    
RMS_6CH_MULT:  A list of 6 values, one for each channel, or one value applied
    to all channels.  This value is multiplied by the RMS voltage reading of
    the channel to give the final sensor value.  If this setting is not present
    in the Settings file, the multiplier defaults to 1.0.

Python packages needed beyond the base mini-monitor packages.  Use
"sudo pip3 install" to install these:
    RPI.GPIO
    adafruit-blinka
    adafruit-circuitpython-ads1x15


Also, 
    sudo apt-get install python3-numpy 
    sudo apt-get install python3-smbus    # not really sure necessary
    sudo apt-get install i2c-tools        # just helpful, not necessary

i2c must enabled via the sudo raspi-config utility.

sudo i2cdetect -y 1
will show the i2c device addresses present.
"""

import time
from . import base_reader
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

SAMPLES = 500  # samples per channel to calculate RMS
RATE = 3300    # samples/second, fastest rate available

class RMS_6ch(base_reader.Reader):
    
    def __init__(self,  settings=None):
        """'settings' is the general settings file for the application.
        """
        # Call constructor of base class
        super(RMS_6ch, self).__init__(settings)
        
        # Get channel gain and multipliers from the settings file if they
        # are present.
        if hasattr(settings, 'RMS_6CH_GAIN'):
            try:
                self._gain = list(settings.RMS_6CH_GAIN)
            except:
                # Must have been a scalar instead of a list or tuple
                self._gain = [settings.RMS_6CH_GAIN] * 6
        else:
            # Nothing the settings file, so default to gain of 1
            self._gain = [1] * 6
            
        if hasattr(settings, 'RMS_6CH_MULT'):
            try:
                self._mult = list(settings.RMS_6CH_MULT)
            except:
                # must have been a scalar instead of a list or tuple
                self._mult = [float(settings.RMS_6CH_MULT)] * 6
        else:
            self._mult = [1.0] * 6
        
    def read(self):

        
        # Channels to cycle through and read, along with channel number identifier
        channels = [
            (ADS.P0, 0),
            (ADS.P1, 1),
            (ADS.P2, 2)
        ]

        # use the same timestamp for all six channels
        ts = time.time()
        data = [None] * SAMPLES
        readings = []

        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        ix = 0
        for addr in (0x48, 0x49):

            # Create the ADC object using the I2C bus
            ads = ADS.ADS1015(i2c, address=addr)
            ads.mode = Mode.CONTINUOUS
            ads.data_rate = RATE
            
            for ads_ch in (ADS.P0, ADS.P1, ADS.P2):
                
                sensor_id = f'{self._settings.LOGGER_ID}_rms_ch{ix + 1}'

                ads.gain = self._gain[ix]
                # Create differential input between this channel and channel 3.
                chan = AnalogIn(ads, ads_ch, ADS.P3)

                for i in range(SAMPLES):
                    data[i] = chan.voltage
                arr = np.array(data)
                arr2 = arr * arr
                rms = arr2.mean() ** 0.5
                readings.append((ts, 
                                 sensor_id, 
                                 rms * self._mult[ix], 
                                 base_reader.VALUE)
                               )
                ix += 1

        return readings
