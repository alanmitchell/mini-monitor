#!/usr/bin/env python3
"""
Class to convert Thermistor readings into temperatures. Also has a
class method that determines an unknown resistance in a divider
network.
"""

from math import log

# Steinhart-Hart Coefficients for various thermistors
coeff = {
'Tekmar 071': (0.001124476, 0.00023482, 8.54409E-08),
'Sure 10K': (0.00090296, 0.000249878, 1.9712E-07),
'US Sensor 5K': (0.00128637, 0.00023595, 9.3841E-08),
'US Sensor J': (0.001128437, 0.000234244, 8.71364E-08),
'BAPI 10K-3': (0.001028172, 0.0002392811, 1.5611865E-07),
'InOut': (0.00131413, 0.000174074, 5.576999E-07),
'Quality 10K Z': (0.001125161025848, 0.000234721098632, 8.5877049E-08),
'ACR': (0.00105135, 0.0002475590, 2.8879777e-08),
'Quality 10K S': (0.001028267, 0.000239267, 1.561795e-07),
}

class Thermistor:

    def __init__(self, thermName, appliedV=5.0, dividerR=10000.0):
        '''
        'thermName' identifies the thermistor type and is the key into 
            the coefficient dictionary (coeff)
        'appliedV' is the voltage applied to the divider network, or,
            alternatively, the A/D count associated with the applied voltage.
        'dividerR' is the resistance in ohms of the fixed divider resistor.
        '''
        self.coeff = coeff[thermName]
        self.thermName = thermName
        self.appliedV = appliedV
        self.dividerR = dividerR
	
    def TfromR(self, resis, unit='F'):
        """
        Returns temperature from a thermistor resistance in ohms.  'unit' can be 'F' or 'C'
        for Fahrenheit or Celsius.
        """
        C1 = self.coeff[0]
        C2 = self.coeff[1]
        C3 = self.coeff[2]
        lnR = log(resis) if resis>0.0 else -9.99e99
        tempF = (1.8 / (C1 + C2 * lnR + C3 * lnR ** 3)) - 459.67
        if unit=='F':
            return tempF
        else:
            return (tempF - 32.0)/1.8

    def TfromV(self, measuredV, appliedV=None, unit='F'):
        """
        Returns a temperature given a measured voltage from a divider network,
        If 'appliedV', the voltage applied to the divider network, is given, the 
        applied voltage supplied in the constructor of this class is overridden.
        'unit' can be 'F' (Fahrenheit) or 'C' (Celsius).
        """
        resis = self.RfromV(measuredV, appliedV)
        return self.TfromR(resis, unit)
    	
    def RfromV(self, measuredV, appliedV=None):
        """
        Returns resistance when given a measured voltage (or A/D count) from a 
        divider circuit with divider resistance 'self.dividerR'. 'appliedV' is the 
        voltage (or A/D count) applied to the divider network; uses object-level
        appliedV if not present in parameter list.
        """
        appV = appliedV if appliedV else self.appliedV
        divV = appV - measuredV
        # protect against divide by 0
        if divV>0:
            return measuredV/divV * self.dividerR
        else:
            return 9.99e99   # something very big


if __name__=='__main__':

   t = Thermistor('Sure 10K')
   print(t.TfromR(35360, 'C'))

   t = Thermistor('US Sensor 5K')
   print(t.TfromR(27665, 'C'))

   t = Thermistor('US Sensor J')
   print(t.TfromR(2157, 'C'))

   t = Thermistor('Tekmar 071')
   print(t.TfromR(6532, 'C'))

   t = Thermistor('Tekmar 071', appliedV=4.73, dividerR=20500.0)
   while 1:
      v = float(input('Enter voltage: '))
      print(t.TfromV(v, unit='F'))
