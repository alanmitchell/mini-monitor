"""Tests state and counter reading types.
"""

import random, time
import base_reader

class TestCounterState(base_reader.Reader):
    
    def __init__(self, settings=None):
        
        # Call constructor of base class
        super(TestCounterState, self).__init__(settings)
        
        self.state = 0
        self.count = 0
    
    def read(self):
        
        readings = []
        ts = time.time()
        
        # counter
        self.count += int(random.random()*10.0)
        readings.append( (ts, 'counter1', self.count, base_reader.COUNTER) )
        
        # state
        if random.random() < 0.1:
            self.state = self.state * -1 + 1
            
        readings.append( (ts, 'state1', self.state, base_reader.STATE) )
        
        return readings