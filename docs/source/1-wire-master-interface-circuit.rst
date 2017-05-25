.. _1-wire-master-interface-circuit:

1-Wire Master Interface Circuit
===============================

Here is the schematic of the circuit that interfaces the 1-Wire
sensors with the USB port on the Raspberry Pi.

.. image:: /_static/1wire_schematic.jpg

The circuit can be built in two different ways. *Option 1* is the
circuit currently being used in Mini-Monitor installations. It utilizes
the `HA7S 1-Wire Module <http://www.embeddeddatasystems.com/HA7S--ASCII-TTL-1-Wire-Host-Adapter-SIP\_p\_23.html>`_,
which is on its last production run. The correct Reader for this is ``ha7s.HA7Sreader``. When this
module becomes unavailable, *Option 2* can be utilized,
although a Reader file has not been finalized for this option; the
``onewire.OneWireReader`` using the OWFS one-wire library will be the
starting point for developing this new Reader.

The Parts list for this circuit is available in this :download:`Excel
Workbook </_static/1wire_bom.xlsx>`. A 5 VDC power supply plugs into the
circuit to power the one-wire sensors that require power (DS18B20
temperature sensors do not require power; Analysis North Motor Sensors
do). Current demands are generally less than 100 mA. A
power supply separate from the Raspberry Pi supply was necessary in many
situations due to transients and noise collected on the sensor power
line that interfered with the operation of USB peripherals and the Pi.

Bare circuit boards can be ordered from `OSH Park <https://oshpark.com/shared_projects/cqbJmohq>`_ at a very affordable
price (three boards for $18.20).

Fully assembled units can be purchased from `Analysis North <http://analysisnorth.com/>`_.

Here is a picture of the assembled circuit board for Option 1:

.. image:: /_static/1wire-pcb.jpg

Here is a picture of the circuit assembled in the case:

.. image:: /_static/1wire-assembled.jpg
