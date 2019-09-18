#!/usr/bin/env python3
'''Module used to read sensor values from a Sensaphone IMS-4000 system.
If changes need to be made, it is helpful to download the free MIB browser available at:
http://www.ireasoning.com/ . To use this properly you have to "Load mib" and then load
the IMS-4000 MIB available from Sensaphone's website.
'''

import time
import logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from . import base_reader


class SensaphoneReader(base_reader.Reader):
    """Class to read sensor and status values from an IMS-4000 Sensaphone host unit.
    """
    # The highest valid node
    NODE_MAX = 32

    def get_value_list(self, oid):
        '''Reuturns a list of values at the object id, 'oid'.  If an error occurs
        an empty list is returned.
        '''

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.bulkCmd(
            cmdgen.CommunityData('public', mpModel=0),
            cmdgen.UdpTransportTarget((self.host_ip, 161)),
            0, 1,
            oid
        )

        val_list = []

        if errorIndication:
            logging.exception('Error reading value list at OID %s: %s' % (oid, errorIndication))
        else:
            if errorStatus:
                err_msg = 'Error reading OID %s: %s at %s' % (
                    oid,
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                logging.exception(err_msg)
            else:
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        if val.prettyPrint().startswith('No more var'):
                            break
                        else:
                            val_list.append(val)
        return val_list

    def getNodeData(self, node):
        '''Returns a list of two-tuples (sensor name, value) for a particular
        'node'.  'node' is a number from 2 to NODE_MAX.
        '''

        # Get list of sensor names
        rd_name_oid = '.1.3.6.1.4.1.8338.1.1.1.%d.8.1.1.2' % node
        rd_name_list = [val.prettyPrint() for val in self.get_value_list(rd_name_oid)]

        # Get associated values for each sensor
        rd_val_oid = '.1.3.6.1.4.1.8338.1.1.1.%d.8.1.1.7' % node
        rd_val_list = [int(val) for val in self.get_value_list(rd_val_oid)]

        return list(zip(rd_name_list, rd_val_list))

    def get1value(self, oid):
        '''Gets a single value for an object id, 'oid' from the sensaphone unit.
        Returns None if an error occurs.
        '''

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((self.host_ip, 161)),
            oid
        )

        value = None    # will be overridden unless an error occurs

        # Check for errors and print out results
        if errorIndication:
            logging.exception('Error reading OID %s: %s' % (oid, errorIndication))
        else:
            if errorStatus:
                err_msg = 'Error reading OID %s: %s at %s' % (
                    oid,
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                logging.exception(err_msg)
            else:
                for name, val in varBinds:
                    value = val

        return value

    def read(self):
        '''Reads in the values from all nodes on a sensaphone with the given host ip.
        '''

        readings = []

        # pull the HOST IP address from the settings file and store as an object
        # variable.
        self.host_ip = self._settings.SENSAPHONE_HOST_IP

        # Note: the range starts at 2 because there is nothing at zero, and 1 is the number for the Host unit, which
        # only has sensors for the battery and sound.
        for node in range(2, SensaphoneReader.NODE_MAX + 1):

            node_ip_oid = '.1.3.6.1.4.1.8338.1.1.1.%s.10.1.0' % node
            node_ip = self.get1value(node_ip_oid)
            if node_ip == '0.0.0.0' or node_ip is None:
                # no more nodes to read if we got a 0.0.0.0 IP address or
                # an Error occurred.
                # we're all done.
                break

            # Get the plain text name of this node
            node_name_oid = '.1.3.6.1.4.1.8338.1.1.1.%s.10.2.0' % node
            node_name = self.get1value(node_name_oid)

            ts = time.time()     # use the same timestamp for all the readings from this node
            name_val_tuples = self.getNodeData(node)
            for rd_name, rd_val in name_val_tuples:
                # create a unique Sensor ID for this sensor
                sensor_id = '%s_%s_%s' % (self._settings.LOGGER_ID,
                                          node_name,
                                          rd_name)
                # replace spaces with underscore in the Sensor ID
                sensor_id = sensor_id.replace(' ', '_')

                readings.append((ts, sensor_id, rd_val, base_reader.VALUE))

        return readings


if __name__ == '__main__':
    from pprint import pprint

    # Create a Settings object to test with.  Normally, these settings will appear in the main
    # settings file for the logger.
    test_settings = base_reader.DummySettings()
    test_settings.SENSAPHONE_HOST_IP = '10.30.5.77'

    rdr = SensaphoneReader(settings=test_settings)
    pprint(rdr.read())
