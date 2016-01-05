#!/usr/bin/python
'''Module used to read sensor values from a Sensaphone IMS-4000 system.
'''

from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import base_reader

# Settings: Ensure that the sensaphone host ip address is correct, name this particular
# sensaphone unit, and put in the maximum number of nodes.
# If changes need to be made, it is helpful to download the free MIB browser available at:
# http://www.ireasoning.com/ . To use this properly you have to "Load mib" and then load
# the IMS-4000 MIB available from Sensaphone's website.
sensaphone_host_ip = '10.30.5.77'
hostname = 'YKHC'
node_max = 31


class SensaphoneReader(base_reader.Reader):
    """Class to read sensor and status values from an IMS-4000 Sensaphone host unit.
    """

    def add_reading(self, hostname, node_name, sensaphone_host_ip, rd_name, rd_val, rd_type=base_reader.VALUE):

            # Creates a list of readings for one node.
            readings = []
            sensor_id = '%s_%s_%s' % (hostname, self.get1value(node_name, sensaphone_host_ip), rd_name)
            readings.append((time.time(), sensor_id, rd_val, rd_type))

            return readings

    def getNodeData(self, node, sensaphone_host_ip):

        # Set object id for this particular node
        rd_name_oid = '.1.3.6.1.4.1.8338.1.1.1.' + str(node) + '.8.1.1.2'
        rd_val_oid = '.1.3.6.1.4.1.8338.1.1.1.' + str(node) + '.8.1.1.7'

        # Get list of sensor names
        rd_name_list = []

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.bulkCmd(
            cmdgen.CommunityData('public', mpModel=0),
            cmdgen.UdpTransportTarget((sensaphone_host_ip, 161)),
            0, 1,
            rd_name_oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                    )
                )
            else:
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        if val.prettyPrint() == 'No more variables left in this MIB View':
                            break
                        else:
                            rd_name_list.append(val.prettyPrint())

        # Get associated values for each sensor
        rd_val_list = []

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.bulkCmd(
            cmdgen.CommunityData('public', mpModel=0),
            cmdgen.UdpTransportTarget((sensaphone_host_ip, 161)),
            0, 1,
            rd_val_oid
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                    )
                )
            else:
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        if val.prettyPrint() == 'No more variables left in this MIB View':
                            break
                        else:
                            rd_val_list.append(int(val))

        name_val_tuple = zip(rd_name_list, rd_val_list)

        return name_val_tuple

    def get1value(self, oid, senaphone_host_ip):
    # Gets a single value for an object id from the sensaphone unit

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((sensaphone_host_ip, 161)),
            oid
        )

        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for name, val in varBinds:
                    value = val

        return value

    def read(self, sensaphone_host_ip, hostname, node_max):
        # Reads in the values from all nodes on a sensaphone with the given host ip.

        self.readings = []

        # Note: the range starts at 2 because there is nothing at zero, and 1 is the number for the Host unit, which
        # only has sensors for the battery and sound.

        for node in xrange(2, node_max):

            node_ip_oid = '.1.3.6.1.4.1.8338.1.1.1.' + str(node) + '.10.1.0'
            node_name_oid = '.1.3.6.1.4.1.8338.1.1.1.' + str(node) + '.10.2.0'

            if self.get1value(node_ip_oid, sensaphone_host_ip) == '0.0.0.0':
                break

            else:
                name_val_tuple = self.getNodeData(node, sensaphone_host_ip)
                for rd_name, rd_val in name_val_tuple:
                    self.readings.append(self.add_reading(hostname, node_name_oid, sensaphone_host_ip, rd_name, rd_val))

        return self.readings


if __name__ == '__main__':
    from pprint import pprint
    rdr = SensaphoneReader()
    pprint(rdr.read(sensaphone_host_ip, hostname, node_max))
