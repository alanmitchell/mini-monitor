#!/usr/bin/python2.6
'''
Creates a MyU3 class that adds higher-level functionality to the base 
LabJack U3 class.
'''


import u3
from time import sleep
import math
from functools import reduce

def getU3(**kargs):
   '''Returns an open MyU3 object but retries until successful if errors occur.'''

   while True:
      try:
         return MyU3(**kargs)
      except:
         sleep(2)
         print('Trying to Open U3...')
   

class MyU3(u3.U3):
   '''
   Class that adds some functionality to the base u3.U3 class, which
   operates a U3 data acquisition device.
   '''

   def __init__(self, **kargs):

      # call the constructor in the base class
      u3.U3.__init__(self, **kargs)


   def getRMS(self, ch, signalFreq=60, numCycles=4):
      '''
      Returns the RMS voltage of a stream of readings on a channel.
      'ch' is the channel to sample.
      'signalFreq' is the fundamental frequency of the signal being sampled.
      'numCycles' is the number of full cycles of the signal that you want to 
         sample for purposes of calculating the RMS value.
      I found that for 60 Hz signals, sampling 4 cycles produces stable
      readings.
      NOTE:  there are limits to the frequency calculation below.  Getting
      a packet from the U3 in streaming mode is limited to 1 second I think, 
      and it will reduces the # of samples if the frequency is set so that
      less than 1200 samples arrive in 1 second.
      '''
      
      # There are 1200 samples in one streaming request of the U3.  Calculate
      # the required streaming frequency from that and the other input parameters.
      freq = int(signalFreq / numCycles * 1200.0)
      freq = min(50000, freq)    # cap at 50 kHz
      

      # the U3 must operate at lower resolution if the streaming is very fast.
      if freq < 2500:
         resolution = 0
      elif freq < 10000:
         resolution = 1
      elif freq < 20000:
         resolution = 2
      else:
         resolution = 3

      self.streamConfig( NumChannels = 1, 
                      PChannels = [ ch ], 
                      NChannels = [ 31 ],     # 31 indicates single-ended read
                      Resolution = resolution, 
                      SampleFrequency = freq )
      try:
         self.streamStart()
          
         for r in self.streamData():

            # calculate the sum of the squares, average that, and take square root
            # to determine RMS
            vals = r['AIN' + str(ch)]
            sum_sqr = reduce(lambda x,y: x + y*y, vals, 0.0)
            return math.sqrt(sum_sqr / len(vals))

      finally:
         self.streamStop()


   def getAvg(self, ch, reads=8, specialRange=False, longSettle=True):
      '''
      Returns an analog reading of channel 'ch', but samples
      multiple times = 'reads' and then averages.  If 'specialRange'
      is True, uses the higher voltage range for the channel.
      If 'longSettle' is True, a higher source impedance can be tolerated.
      '''
      if specialRange:
         negCh = 32
      else:
         negCh = 31
      
      tot = 0.0
      for i in range(reads):
         tot += self.getAIN(ch, negCh, longSettle=longSettle)
      return tot / reads
      
   # Could add a routine to average an analog reading across 
   # 4 60 Hz cycles using the stream function as in getRMS().

   def getDutyCycle(self, timer, reads=8):
      '''
      Returns the duty cycle measured by a timer.  Assumes that the timer is already
      set to Mode = 4 for reading duty cycles.
      timer - the timer number, either 0 or 1.
      reads - the number of times to read the duty cycle and average
      '''
      tot = 0.0    # used to average the duty cycle readings
      for i in range(reads):
         val = self.getFeedback(u3.Timer(timer=timer))[0]
         hi = float(val % 2**16)
         lo = float(val / 2**16)
         tot += hi / (lo + hi)
      return tot / reads
      

if __name__=='__main__':

   # create the device object
   d = MyU3()

   # Set all possible inputs to Analog
   # Create a bit mask indicating which channels are analog:
   FIOEIOAnalog = ( 2 ** 16 ) - 1;  
   fios = FIOEIOAnalog & (0xFF)     # the bottom 8 bits
   eios = FIOEIOAnalog/256          # shift 8 places to get top 8 bits
   d.configIO( FIOAnalog = fios, EIOAnalog = int(eios) )

   try:
      while True:
            #print '%.3f' % d.getAvg(6)
            #print '%.2f' % ( (d.getAvg(30) - 273.15)*1.8 + 32.0 )
            print('%.3f' % d.getRMS(6))
            sleep(0.5)
   finally:
      d.close()