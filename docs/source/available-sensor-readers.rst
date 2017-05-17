.. _available-sensor-readers:

Available Sensor Readers
========================


This document summarizes the Sensor Reader classes that are currently
available for the Mini-Monitor. Each of these classes knows how to read
data from a particular type of device. As described on the main
:ref:`software` document, a Reader is enabled in the ``READERS`` variable found
in the Mini-Monitor settings file.

Starting with Version 1.7, Mini-Monitor has an additional method to
acquire sensor data, separate from the Sensor Reader classes described
in the prior paragraph. Scripts or programs can be written to publish
data to the Mini-Monitor MQTT broker (for more about the MQTT broker,
see the :ref:`Notes for Developers <developers>`. That sensor data is then
posted directly to a BMON server without the use of a Reader class.
This technique is used to read data from Utility Meters, this script 
is discussed later in this document.

Sensor Reader Classes
---------------------

Each section below describes a Reader and lists the sensor information
that is returned by the Reader. For each sensor read by the Reader, the
following information is returned:

**Sensor ID**: This is a string ID that identifies the particular sensor
being read.

**Value**: This is the current numeric sensor reading.

**Reading Type**: This indicates the type of value being read by the
sensor, with the following three possibilities:

*  **VALUE**: An analog value that varies continuously across a range of
   possible values. For this Reading Type, the Mini-Monitor will average
   all of the sensor values that are read during a logging period and
   post that average value to the BMON web database.
*  **STATE**: Discrete values that indicate the
   sensor is in a particular mode or state. Examples include On/Off
   switch values, or alarm states for a particular device. During one
   logging period, the Mini-Monitor will post a reading to BMON 
   every time the sensor state value changes. In addition, the
   Mini-Monitor will always post the last state value read during the
   logging period.
*  **COUNTER**: A sensor having a Reading Type of counter is one that
   accumulates a count of some quantity, e.g. energy used or gallons of
   flow. For counter sensors, the Mini-Monitor will post the last
   counter value read during a logging period.

Currently Available Sensor Readers
==================================

1-Wire Sensor Reader
--------------------

**Class Name:** ``ha7s.HA7Sreader`` (named after the Embedded Data Systems HA7S hardware module used to read the 1-Wire sensors).

This Reader reads `Maxim DS18B20 1-Wire Temperature Sensors (Family Code 28) <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS18B20.html>`_
and sensors utilizing the `Maxim DS2406 1-Wire chip (Family Code 12) <http://www.maximintegrated.com/en/products/digital/memory-products/DS2406.html>`_
to sense the On/Off state of a device. `Analysis North <http://analysisnorth.com>`_ sells an easily-installed
motor/pump/zone valve/gas valve sensor utilizing this chip that can interface to the Mini-Monitor through the 1-Wire network.

The Mini-Monitor hardware components associated with this Reader are the CV3
and PS2 components described in the :ref:`hardware` document. The Reader
returns the current sensor readings for all of the compatible 1-Wire
sensors on the network. The table below shows the information returned
for each compatible type of 1-Wire sensor:

+----------------+-------------+---------+--------------+
| Sensor Type    | Sensor ID   | Value   | Reading Type |
+================+=============+=========+==============+
| Family Code 28 | Unique      | Tempera | VALUE        |
| Temperature    | 1-Wire ID   | ture    |              |
| Sensors        | of the      | in      |              |
|                | Sensor,     | degrees |              |
|                | e.g.        | F       |              |
|                | ``28.EFED4C |         |              |
|                | 050000``    |         |              |
+----------------+-------------+---------+--------------+
| Family Code 12 | Unique      | The     | STATE        |
| Switch/State   | 1-Wire ID   | state   |              |
| Sensors        | of the      | of      |              |
|                | Sensor,     | Channel |              |
|                | e.g.        | A of    |              |
|                | ``12.FDF4A0 | the     |              |
|                | 000000``    | Sensor: |              |
|                |             | 1 for   |              |
|                |             | High    |              |
|                |             | Voltage |              |
|                |             | ,       |              |
|                |             | 0 for   |              |
|                |             | Low     |              |
|                |             | Voltage |              |
|                |             | .       |              |
+----------------+-------------+---------+--------------+

Sage 2.1 Boiler Control (used in Burnham Alpine Boilers)
--------------------------------------------------------

**Class Name:** ``sage_boiler.Sage21Reader``

This reader reads numerous values present in a Sage 2.1 Boiler Control,
which is the boiler control used by the Burnham Alpine condensing
boilers. The values are read through an RS485 connection to the boiler,
using the MODBUS protocol. The Sage 2.1 control is manufactured by
Honeywell and is known as the SOLA control when sold directly by
Honeywell. `Here is the MODBUS manual <https://customer.honeywell.com/resources/Techlit/TechLitDocuments/65-0000s/65-0310.pdf>`_
for the Honeywell SOLA boiler controller.

The RS485 connection to the boiler is on the left side of the boiler.
There are two RJ45 jacks (8-pin network-type jacks). Standard CAT-5/6
network cable can be used to connect to the boiler, and the **top**
jack, labeled "BOILER TO BOILER" must be used. Also, you must set the
"Boiler Address" to 1 in order to read data from the boiler. This is
done on the "Adjust", "Sequence Slave", "Boiler Address" menu item
available through the touch screen control on the boiler. The Factory
default for this setting is "None", so it must be changed in order for
the monitoring system to work.

The table below shows the values that are read from the controller.
Refer to MODBUS manual for more detail on the values. The ``Sensor ID``
values all start with the ``<LOGGER_ID>``, which is the unique ID value
that is entered into the Mini-Monitor settings file, as described in the
:ref:`software` document. For example, if the ``LOGGER_ID`` for a paricular
Mini-Monitor is ``Burton152``, the first sensor value in the table below
will have the Sensor ID of ``Burton152_firing_rate``.

+-------------+---------+-----------------+
| Sensor ID   | Value   | Reading Type    |
+=============+=========+=================+
| <LOGGER\_ID | Boiler  | STATE           |
| >\_alert\_c | alert   |                 |
| ode         | code,   |                 |
|             | if any; |                 |
|             | see     |                 |
|             | Table   |                 |
|             | 11 in   |                 |
|             | MODBUS  |                 |
|             | manual. |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | VALUE           |
| >\_firing\_ | firing  |                 |
| rate        | rate in |                 |
|             | % of    |                 |
|             | maximum |                 |
|             | .       |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Indicat | STATE           |
| >\_limits   | es      |                 |
|             | when a  |                 |
|             | Boiler  |                 |
|             | Limit,  |                 |
|             | such as |                 |
|             | Outlet  |                 |
|             | High    |                 |
|             | Tempera |                 |
|             | ture    |                 |
|             | Limit,  |                 |
|             | is      |                 |
|             | reached |                 |
|             | .       |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Source  | STATE           |
| >\_demand\_ | of      |                 |
| source      | demand  |                 |
|             | that    |                 |
|             | caused  |                 |
|             | the     |                 |
|             | boiler  |                 |
|             | to      |                 |
|             | fire,   |                 |
|             | either  |                 |
|             | Space   |                 |
|             | Heat or |                 |
|             | Domesti |                 |
|             | c       |                 |
|             | Hot     |                 |
|             | Water   |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | VALUE           |
| >\_outlet\_ | outlet  |                 |
| temp        | tempera |                 |
|             | ture,   |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Flame   | VALUE           |
| >\_flame\_s | signal, |                 |
| ignal       | Volts.  |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | VALUE           |
| >\_inlet\_t | return  |                 |
| emp         | water   |                 |
|             | tempera |                 |
|             | ture,   |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | VALUE           |
| >\_stack\_t | stack   |                 |
| emp         | tempera |                 |
|             | ture,   |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Space   | VALUE           |
| >\_ch\_setp | Heating |                 |
| oint        | boiler  |                 |
|             | tempera |                 |
|             | ture    |                 |
|             | setpoin |                 |
|             | t,      |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | DHW     | VALUE           |
| >\_dhw\_set | boiler  |                 |
| point       | tempera |                 |
|             | ture    |                 |
|             | setpoin |                 |
|             | t,      |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Current | VALUE           |
| >\_active\_ | ly      |                 |
| setpoint    | active  |                 |
|             | boiler  |                 |
|             | setpoin |                 |
|             | t,      |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | STATE           |
| >\_lockout\ | Lockout |                 |
| _code       | code,   |                 |
|             | if any; |                 |
|             | see     |                 |
|             | Table 9 |                 |
|             | in      |                 |
|             | MODBUS  |                 |
|             | manual. |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Indicat | STATE           |
| >\_alarm\_r | es      |                 |
| eason       | whether |                 |
|             | the     |                 |
|             | Alarm   |                 |
|             | is a    |                 |
|             | Lockout |                 |
|             | or an   |                 |
|             | Alert.  |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Indicat | STATE           |
| >\_ch\_dema | es      |                 |
| nd          | if      |                 |
|             | there   |                 |
|             | is a    |                 |
|             | call    |                 |
|             | for     |                 |
|             | Space   |                 |
|             | Heat.   |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Indicat | STATE           |
| >\_dhw\_dem | es      |                 |
| and         | if      |                 |
|             | there   |                 |
|             | is a    |                 |
|             | call    |                 |
|             | for DHW |                 |
|             | heat.   |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Outdoor | VALUE           |
| >\_outdoor\ | tempera |                 |
| _temp       | ture,   |                 |
|             | as read |                 |
|             | by      |                 |
|             | boiler  |                 |
|             | outdoor |                 |
|             | tempera |                 |
|             | ture    |                 |
|             | sensor, |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Boiler  | STATE           |
| >\_alarm\_c | alarm   |                 |
| ode         | code,   |                 |
|             | if any. |                 |
+-------------+---------+-----------------+

AERCO BMS II Boiler Manager
---------------------------

**Class Name:** ``aerco_boiler.BMS2reader``

This reader reads values present in an AERCO BMS II Boiler Manager,
which controls a bank of AERCO boilers. The `AERCO BMS II manual is
here <http://www.aerco.com/DocumentRepository/Download.aspx?file=1809>`_,
and Appendix H contains documentation of the MODBUS registers. The
Reader obtains values from the controller using the MODBUS protocol
across an RS232 connection to the boiler.

The table below shows the values that are read from the controller.
Refer to the BMS II manual for more detail on the values. The
``Sensor ID`` values all start with the ``<LOGGER_ID>``, which is the
unique ID value that is entered into the Mini-Monitor settings file, as
described in the :ref:`software` page.

+-------------+---------+-----------------+
| Sensor ID   | Value   | Reading Type    |
+=============+=========+=================+
| <LOGGER\_ID | Firing  | VALUE           |
| >\_firing\_ | rate as |                 |
| rate        | a % of  |                 |
|             | maximum |                 |
|             | .       |                 |
|             | All     |                 |
|             | boilers |                 |
|             | fired   |                 |
|             | have    |                 |
|             | this    |                 |
|             | same    |                 |
|             | firing  |                 |
|             | rate,   |                 |
|             | as the  |                 |
|             | load is |                 |
|             | spread  |                 |
|             | evenly  |                 |
|             | across  |                 |
|             | fired   |                 |
|             | boilers |                 |
|             | .       |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | The     | STATE           |
| >\_boilers\ | number  |                 |
| _fired      | of      |                 |
|             | boilers |                 |
|             | current |                 |
|             | ly      |                 |
|             | fired.  |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | The     | VALUE           |
| >\_firing\_ | firing  |                 |
| rate\_tot   | rate    |                 |
|             | times   |                 |
|             | the     |                 |
|             | number  |                 |
|             | of      |                 |
|             | boilers |                 |
|             | fired,  |                 |
|             | %.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Tempera | VALUE           |
| >\_header\_ | ture    |                 |
| temp        | of the  |                 |
|             | boiler  |                 |
|             | outlet  |                 |
|             | header, |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Outdoor | VALUE           |
| >\_outdoor\ | tempera |                 |
| _temp       | ture    |                 |
|             | as read |                 |
|             | by the  |                 |
|             | control |                 |
|             | ler     |                 |
|             | outdoor |                 |
|             | tempera |                 |
|             | ture    |                 |
|             | sensor, |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Target  | VALUE           |
| >\_header\_ | setpoin |                 |
| setpoint    | t       |                 |
|             | tempera |                 |
|             | ture    |                 |
|             | for the |                 |
|             | boiler  |                 |
|             | outlet  |                 |
|             | header, |                 |
|             | degrees |                 |
|             | F.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Number  | STATE           |
| >\_boilers\ | of      |                 |
| _online     | boilers |                 |
|             | online  |                 |
|             | and     |                 |
|             | able to |                 |
|             | be      |                 |
|             | fired.  |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Indicat | STATE           |
| >\_fault\_c | es      |                 |
| ode         | type of |                 |
|             | fault   |                 |
|             | that    |                 |
|             | has     |                 |
|             | occurre |                 |
|             | d.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Number  | STATE           |
| >\_lead\_bo | of the  |                 |
| iler        | Lead    |                 |
|             | boiler, |                 |
|             | 1 - 32. |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Gives   | STATE           |
| >\_boiler1\ | online  |                 |
| _status     | and     |                 |
|             | firing  |                 |
|             | status  |                 |
|             | of      |                 |
|             | Boiler  |                 |
|             | #1.     |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Gives   | STATE           |
| >\_boiler2\ | online  |                 |
| _status     | and     |                 |
|             | firing  |                 |
|             | status  |                 |
|             | of      |                 |
|             | Boiler  |                 |
|             | #2.     |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Gives   | STATE           |
| >\_io\_stat | status  |                 |
| us          | of the  |                 |
|             | boiler  |                 |
|             | relays. |                 |
+-------------+---------+-----------------+

Sensaphone Reader
-----------------

**Class Name:** ``SensaphoneReader``

This reader reads values from the Sensaphone Infrastructure Management
System host unit (IMS-4000). The reader uses the `Simple Network
Managmenet Protocol <https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol>`_
(SNMP) to access the IMS-4000 host, which in turn is connected to up to
32 different remote sites. Each remote site can have up to 8
environmental sensors. The manual for the IMS-4000 can be found
`here <http://www.sensaphone.com/pdf/LIT-0064_IMS-4000_Manualv3.0_WEB.pdf>`_.

The reader will access and return data for each of the sensors attached
to each remote site connected to the IMS-4000. There are a variety of
sensors that can be connected at each site, including sensors that
monitor temperature, relative humidity, flow, presence of water, and
more. For details on the values reported by individual sensors, see the
`IMS-4000 manual <http://www.sensaphone.com/pdf/LIT-0064_IMS-4000_Manualv3.0_WEB.pdf>`_.
Each of these sensors is named by the user; the sensor IDs reported in
the mini-monitor program are named using the following pattern:

``<LOGGER_ID>_<Site_Name>_<Sensor_Name>``

Note that underscores are used in place of spaces in this naming
pattern. Currently, due to the limitations of the SNMP interface, all
recorded data is reported as integers of the "VALUES" reading type.

System Information Reader
-------------------------

**Class Name:** ``sys_info.SysInfo``

This Reader reports some basic information about the Mini-Monitor
hardware and software. It reads the values directly from the Raspberry
Pi without the need for any additional attached hardware. Here are the
values reported:

+-------------+---------+-----------------+
| Sensor ID   | Value   | Reading Type    |
+=============+=========+=================+
| <LOGGER\_ID | Number  | COUNTER         |
| >\_uptime   | of      |                 |
|             | seconds |                 |
|             | that    |                 |
|             | the Pi  |                 |
|             | has     |                 |
|             | been    |                 |
|             | operati |                 |
|             | ng      |                 |
|             | since   |                 |
|             | the     |                 |
|             | last    |                 |
|             | reboot. |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | CPU     | VALUE           |
| >\_cpu\_tem | tempera |                 |
| p           | ture    |                 |
|             | of the  |                 |
|             | Pi,     |                 |
|             | degrees |                 |
|             | C.      |                 |
+-------------+---------+-----------------+
| <LOGGER\_ID | Mini-Mo | STATE           |
| >\_version  | nitor   |                 |
|             | softwar |                 |
|             | e       |                 |
|             | version |                 |
|             | number. |                 |
+-------------+---------+-----------------+

Other Sensor Readers
--------------------

There are a number of other sensor readers that have been created for
specific projects and not documented here in detail. Those Readers
include ones for reading thermistors connected to a `Labjack U3 data
acquisition board <http://labjack.com/u3>`_ and reading gauge air
pressure measured by an `Energy Conservatory DG-700 Pressure
Gauge <http://products.energyconservatory.com/dg-700-pressure-and-flow-gauge/>`_.
You can find these in the ``readers`` directory of the `project
code <https://github.com/alanmitchell/mini-monitor/tree/master/readers>`_.

Scripts that Post Data directly to the MQTT Broker
--------------------------------------------------

Script to Read Utility Meter Radio Transmissions
------------------------------------------------

The Mini-Monitor is able to read Utility meters (natural gas, electric,
and water) that utilize the Itron ERT radio transmission format to
broadcast their readings in the 900 MHz ISM band to meter readers
driving through the neighborhood. The hardware required for receiving
these transmissions is described in the :ref:`hardware` document. To
enable and configure the Meter Reading script, see the Mini-Monitor section in the :ref:`Software <software>` document.

Utility meters generally are counters that accumulate the total amount
of gas, electricity, or water consumed. Instead of reporting this
cumulative amount, this script determines the rate of change of the
meter and reports that value, expressed in change in meter reading per
hour. For example, if a natural gas meter reads 10,123 cubic feet at
Noon and then reads 10,145 cubic feet at 12:30 pm, the change in reading
was 22 cubic feet and it occurred over a half hour period. The script
will report a value of 44 cubic feet per hour, since this is the rate of
change expressed using an hourly time base. The BMON server software can
utilize a Transform function to translate that value into BTU/hour, if
desired (the Transform function would be: val \* 1000.0, if the gas
contains 1,000 Btus/cubic foot).

Here is the summary table showing the fields reported by the script. An
example of a Sensor ID for an installation with a ``LOGGER_ID`` of
``123main`` would be ``123main_32707556``. The ``32707556`` is the ID of
the meter, which is generally found on the nameplate of the meter.

+-----------------------------+---------------------------------+----------------+
| Sensor ID                   | Value                           | Reading Type   |
+=============================+=================================+================+
| <LOGGER\_ID>\_<METER\_ID>   | Meter Reading Change per Hour   | VALUE          |
+-----------------------------+---------------------------------+----------------+
