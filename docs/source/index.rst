.. _index:

Mini-Monitor: Raspberry Pi Data Collection System
=================================================

Copyright (c) 2014, Alaska Housing Finance Corporation. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this software except in compliance with the License, as
described in the :ref:`license.rst file <license>`.

The Mini-Monitor software is data acquisition software that runs on a
`Raspberry Pi computer <https://www.raspberrypi.org/>`_. It is designed
to post the collected data to the `BMON web-based sensor reading
database and analysis software <https://github.com/alanmitchell/bmon>`_, but the software can be
modified to post to other Internet databases. The Mini-Monitor software
has the ability to collect data from a number of different sources,
including:

*  `Maxim DS18B20 1-Wire Temperature Sensors <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS18B20.html>`_
*  Sensors utilizing the `Maxim DS2406 1-Wire chip <http://www.maximintegrated.com/en/products/digital/memory-products/DS2406.html>`_
   to sense the On/Off state of a device. `Analysis North <http://analysisnorth.com>`_ sells an easily-installed motor/pump/zone valve/gas valve sensor utilizing this chip that can
   interface to the Mini-Monitor through the 1-Wire network.
*  Utility meters (gas, electric, water) that transmit their meter readings using the Itron ERT radio format.
*  `Burnham Alpine Boilers <http://www.usboiler.net/product/alpine-high-efficiency-condensing-gas-boiler.html>`_
   utilizing the Sage controller. The Mini-Monitor interfaces to the boiler via the boiler's RS-485 Modbus interface and extracts numerous
   sensor and state values from the boiler.
*  The `AERCO BMS II Boiler controller <http://www.aerco.com/Products/Accessories/Controls/BMS-II-Model-5R5-384>`_,
   which controls a set of AERCO boilers. The Raspberry Pi interfaces via a serial RS-232 MODBUS interface.
*  Thermistors connected to a `Labjack U3 data acquisition board <http://labjack.com/u3>`_.
*  `Acurite 592TXR Temperature/Humidity Wireless sensors <https://www.acurite.com/kbase/General/592TXR.html>`_.
*  `Peacefair PZEM-016 Electric Power Sensor <https://community.openenergymonitor.org/t/pzem-016-single-phase-modbus-energy-meter/7780>`_.
*  Gauge air pressure measured by an `Energy Conservatory DG-700 Pressure Gauge <http://products.energyconservatory.com/dg-700-pressure-and-flow-gauge/>`_.
*  Sensaphone's Infrastructure Monitoring System (`IMS-4000 <http://www.sensaphone.com/pdf/LIT-0064_IMS-4000_Manualv3.0_WEB.pdf>`_).
   Data can be obtained from up to 32 remote nodes, each with the capacity to reco`rd 8 different sensors. The Raspberry Pi obtains data
   using the `Simple Network Management Protocol <https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol>`_
   (SNMP).

The software design is flexible and allows for the easy addition of
other data sources. To add a new data source, an appropriate "Reader"
class written in Python must be created, and can then be combined with
other Reader classes to create a customized data acquisition system.

Here is a picture of a Mini-Monitor installed in a boiler room
connecting to a Burnham Alpine Boiler and a string of 1-Wire temperature
and motor sensors:


.. image:: /_static/mini-monitor-installed.jpg

This site holds the documentation for the software. The documentation is
divided into three main sections, described below and available on the
sidebar menu on the lefthand side of this screen.

:ref:`Software <software>`
-------------------------

This section contains documentation for users who wish to install,
configure and use the Mini-Monitor software on a Raspberry Pi computer.

:ref:`Hardware <hardware>`
--------------------------

This section gives details about the hardware components and assembly
required to create a Mini-Monitor system.

:ref:`Developers <developers>`
------------------------------

This section provides documentation for developers who want to modify
the code of the Mini-Monitor system. The source code of the project is
internally documented with comments, but the documentation in this section
explains the overall structure of the application. The repository
holding the source code is `located here <https://github.com/alanmitchell/mini-monitor/>`_.

:ref:`Contact Info <contact-info>`
----------------------------------

Contact information for key Mini-Monitor personnel and developers is
available here.


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Software
   
   software
   available-sensor-readers
   
.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Hardware

   hardware
   configuring-the-dovado-tiny-cellular-router
   1-wire-master-interface-circuit
   1-wire-sensors-and-cabling   
   relevant-manuals
   
.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Developers
   
   developers

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contact Info

   contact-info
