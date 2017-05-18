.. _hardware:

Hardware
========

This section of the Wiki gives details on the hardware components and
interconnection required to build a Mini-Monitor system. The block
diagram below shows the main components of the Mini-Monitor system.

.. figure:: /_static/system-option1.jpg
   Option 1

The Mini-Monitor system needs access to the Internet to post the data
collected by the system. There are a number of options possible for
Internet access including:

*  Direct Ethernet connection to an existing building network that has
   Internet access.
*  Use of a USB WiFi adapter plugged into the Raspberry Pi to access an
   existing WiFi network.
*  Use of a cellular data connection to provide Internet access through
   a mobile wireless network, which is the option shown in the diagram
   and picture above.

More detailed information on Internet access is provided in the `AHFC
Building Monitoring System Design Guidelines
Report <https://github.com/alanmitchell/bmon/wiki/reports/monitoring_system_design_guidelines.pdf>`_,
Section 3.

The components within the dashed box and labeled *Option 1* show the
preferred method of providing a *cellular* data connection to the
Raspberry Pi. A USB Cellular Modem is connected directly to a USB port
on the Raspberry Pi. Configuration of the Modem on the Raspberry Pi is
described in the :ref:`software` document.
Connection tracking software on the Pi combined with a reliable Cellular
Modem make for a relatively robust Internet connection. For added
reliability, the power to the Pi can be periodically cycled using the
Timer Switch (SW1), which is described later.

The diagram below shows an alternative method of providing a cellular
Internet connection to the Raspberry Pi. A cellular router is used in
combination with the cellular modem. The router provides a standard
Ethernet connection to the Raspberry Pi. This Option 2 utilizes more
equipment than Option 1 and is therefore more expensive. Also, we have
yet to find a cellular router model that is both inexpensive and that
provides a reliable Internet connection. There is more discussion below
under the section Part CR1, Cellular Router. Option 2 involving a
cellular router does offer the advantage of providing a WiFi network for
other WiFi-enabled devices such as smart thermostats.

.. figure:: /_static/system-option2.jpg
   Option 2

The picture below shows an assembled version of the Mini-Monitor with
the Option 1 cellular Internet connection. Not all components present in
the block diagram are present in this particular Mini-Monitor. In
particular, the CV2, which is used to read data from an AERCO boiler is
not present, because an AERCO boiler is not present in this building.
Also, the some of the clamp-on ferrite cores, F1 - F4, are not present
in picture. The two power supplies, PS1 and PS2, are outside of the
Mini-Monitor enclosure, so are not shown in the picture. It is also
worth noting that the Mini-Monitor in the picture was constructed with a
Raspberry Pi model B computer (component CO1), but a new installation of
the Mini-Monitor should use the Raspberry Pi 3 Model B.

.. image:: /_static/mini-monitor1.jpg

Below is a picture of the Mini-Monitor with the Option 2 cellular
Internet connection involving the cellular router.

.. image:: /_static/mini-monitor2.jpg

The rest of this document provides additional detail on the components
that make up the Mini-Monitor and provides additional hardware assembly
detail. Software configuration issues are documented elsewhere in this
Wiki.

Part CO1, Raspberry Pi 3 Model B Computer
-----------------------------------------

This is a small Linux computer, available from many different sources.
Here is the `product website <https://www.raspberrypi.org>`_. For new
installations, the Pi 3 Model B should be used, although older models
may work with the software.

We have been using a simple plastic case for the Pi, many are available
and suitable. The model B+ Pi takes a micro-SD card, and the
Mini-Monitor SD card images are meant to fit on an **8 GB micro-SD
Card**. We have typically used cards made by SanDisk.

Part CM1, USB Cell Modem
------------------------

Both Option 1 and Option 2 require use of a Cellular Modem with a USB
interface, pat CM1 in the above diagrams. The cellular modem is the
radio device that actually communicates with the mobile wireless network
and provides a digital interface for that communication.

For Option 1 in the diagrams above, the Sierra Wireless 313U modem has
provided reliable operation with support for 4G (LTE), 3G, and 2G
service from the GCI carrier in Alaska. In late 2016, these modems are
available on Ebay for approximately $50.

For the GCI mobile wireless network, which serves many rural Alaskan
sites, the cellular modem needs to support the 850 MHz and 1900 MHz
frequency bands for 2G (EDGE, GPRS) and 3G (UMTS, HSPA) service. If the
cellular modem supports 4G LTE, it needs to support the LTE AWS Band 4
frequencies, as this is where GCI operates.

For Option2, we have found the following combinations of USB cellular
modems and Dovado Tiny firmwares to be effective:

*  Huawei E173u-6 3G/2G cellular modem with Tiny firmware versions 7.3.4
   operating on the General Communication Inc. (GCI) mobile wireless
   network.
*  Sierra Wireless 313U 4G LTE/3G/2G cellular modem with Tiny firmware
   versions 7.3.4 operating on the General Communication Inc. (GCI)
   mobile wireless network. We have used this modem because we have
   sometimes found that 2G/3G signal strength was insufficient, and a 4G
   LTE modem was required. However, under low signal strength
   conditions, we have experienced lock ups when using this modem with
   the Dovado Tiny router, despite enabling the Dovado Connection
   Tracker. To remedy this, we have used a `clock
   timer <http://www.amazon.com/Woods-50007-Indoor-Digital-Settings/dp/B005WQIDHY/ref=pd_bxgy_60_img_y>`_
   to reboot the Dovado Tiny on a daily basis.

As disucssed in the `Design Guidelines
Report <https://github.com/alanmitchell/bmon/wiki/reports/monitoring_system_design_guidelines.pdf>`_,
the `Option Cloudgate cellular
router <http://www.option.com/#secondPage>`_ has proven to be more
reliable than the Dovado Tiny and it has a cellular modem built in;
however, it is physically larger and more expensive.

Part CR1, Dovado Tiny Cellular Router
-------------------------------------

The cellular router shown in the diagram and picture above is a Dovado
Tiny router. The router requires the use of a separate USB Cellular
Modem, which was described in the above section. We have purchased the
Tiny router through `WirelessGear <https://wirelessgear.com.au/>`_,
located in Australia. The power supply shipped with the router does not
fit US power outlets. We have addressed this by sharing the Raspberry Pi
power supply, PS1, with the Tiny (as discussed later); however, an
alternative is to buy a suitable US-configured power supply, such as
Super Power Supply AC / DC Adapter Cord 5V 2A (2000ma) 3.5mm x 1.35mm
Wall Plug, available through
`Amazon <http://www.amazon.com/Super-Power-Supply%C2%AE-Certified-3-5x1-35mm/dp/B00DHR641M>`_
or EBay. Also, `MovingWiFi <http://movingwifi.com/>`_ out of England
sells the Dovado Tiny router with a US power supply as an option, but
prices have tended to be higher from this source.

For details on configuring the Dovado Tiny router, please see this
article: :ref:`configuring-the-dovado-tiny-cellular-router`.

Part PS1, Power Supply for Raspberry Pi and Dovado Tiny Router
--------------------------------------------------------------

The Power Supply PS1 is used for the Raspberry Pi and for the Dovado
Tiny Router if Option 2 is being built. As mentioned above, it is also
possible to provide a separate power supply for the Tiny router,
requiring an extra AC outlet on the surge protector and an additional
Ferrite core (discussed later) for further surge protection.

The power supply is a wall plug-in type, as shown in the picture below:

.. image:: /_static/ps1_supply.jpg

We particularly like this `Adafruit 5V 2A power
supply <http://www.adafruit.com/products/1995>`_ because it is designed
to put out 5.1 VDC, which is still within specification for the USB
voltage range. Because the relatively high current draw of the Raspberry
Pi and Tiny router, voltage drop occurs between the power supply and the
power-consuming devices. By starting at a slightly higher 5.1 VDC, the
voltage at the devices will stay above minimum requirements.

In order to share the power supply between the Raspberry Pi and the
Dovado Tiny router for Option 2, a Y-splice was made to feed power to
both devices. The power connector for the Tiny router was clipped off
the Australian-format power supply and spliced into the Adafruit supply
cable, as shown in the picture below.

.. image:: /_static/ps1_y_junction.jpg

This junction occurs inside the Mini-Monitor enclosure, so one cable
extends out of the enclosure to the power supply unit. The snap-on
ferrite core is shown in the picture, snapping onto the trunk line back
to the power supply.

Parts F1 - F6, Snap-on Ferrite Cores
------------------------------------

Mechanical rooms are electrically noisy environments. Providing surge
and noise suppression on cables connecting to the Mini-Monitor is
helpful to ensure reliable operation. One easy addition to cables that
help address this problem are snap-on ferrite core filters. There are
five shown in the system diagram above, and they should be mounted in or
very close to the Mini-Monitor enclosure.

**F1 and F5** fit on the two different power supply cables. The power
cables are relatively small, and we use **Laird-Signal Integrity
Products model 28A0350-0B2** for this application, available from
`Digi-Key <http://www.digikey.com/product-search/en?x=0&y=0&lang=en&site=us&keywords=240-2233>`_.

The other cables require Ferrite cores with a larger inner diameter. For
these applications we use **Laird-Signal Integrity Products model
28A2025-0A2**, also available from
`Digi-Key <http://www.digikey.com/product-search/en?KeyWords=240-2075&WT.z_header=search_go>`_.

Timer Switch, Part SW1
----------------------

Sometimes cellular modems, cellular routers, or the Raspberry Pi may
"lock up" and fail to continue operating due to software bugs. This
generally can be remedied by power-cycling the device. Timer Switch SW1
shown in the above diagrams is an optional device that can be used to
improve reliability if software lock-ups are occurring. The Timer Switch
can be programmed to turn Off the Raspberry Pi (and Cellular Modem for
Option 2) for one minute and then back On each day or every few days.
The reboot will generally bring the device out of lock-up. Here are
models that will perform the task:

`Woods 50007-50027 24-Hour Digital Timer <https://www.amazon.com/Woods-50007-24-Hour-Digital-Settings/dp/B005WQIDHY/ref=sr\_1\_1?s=hi&ie=UTF8&qid=1482365792&sr=1-1&keywords=woods+50007>`_

`Woods 50008 7-Day Digital Timer <https://www.amazon.com/Woods-50008-Digital-Programmable-Settings/dp/B006LYHEEY/ref=pd\_sim\_60\_10?\_encoding=UTF8&psc=1&refRID=BXSRCQXK95HM7K3EB6AE>`_

Burnham Alpine Boiler Interface, Parts CV1 and J1
-------------------------------------------------

If you are collecting data from a Burnham Alpine Boiler using the Sage
2.1 controller, you need to connect parts CV1, a USB-to-RS485 converter,
and J1, a punch-down RJ45 jack. The boiler controller has a MODBUS RS485
interface that is accessed through a standard RJ45 jack on the side of
the boiler. For CV1, we use the `EKM Blink - RS-485 to USB Converter <http://www.ekmmetering.com/ekm-blink-rs-485-to-usb-converter.html>`_,
available direct from EKM Metering or on Ebay. If you choose to
substitute a different USB-to-RS485 converter, it must utilize an FTDI
converter chip to work with the Mini-Monitor software.

The EKM Blink RS485 converter has screw terminal connections. The cable
to the Burnham boiler is a conventional CAT-5 or CAT-6 patch cable with
RJ45 connectors on each end. To allow for an RJ45 connection at the
Mini-Monitor, we use a punch down RJ45 jack such as the `Monoprice
Surface Mount Box Cat6, Single
(107092) <http://www.amazon.com/gp/product/B005E2Y9WY>`_. This is J1 on
the system diagram and Mini-Monitor picture above.

There are two connections required from the EKM RS485 converter to the
RJ45 jack: the **+** connection on RS485 converter goes to **pin 8** of
the RJ45, and **-** connection goes to **pin 7**.

Note the Snap-On Ferrite Core, F2, that should be placed on the CAT-5/6
cable to the boiler.

AERCO Boiler Manager BMS II Interface, Part CV2
-----------------------------------------------

If you are collecting data from an `AERCO BMS II Boiler Management
System <http://www.aerco.com/Products/Accessories/Controls/BMS-II-Model-5R5-384>`_,
you need to install CV2, a USB-to-RS232 converter. The model we used is
the `USBGear USB to Serial Adapter, 9-pin male available from
Amazon <http://www.amazon.com/gp/product/B003RWWZAQ>`_. If you
substitute a different converter, it must use an FTDI chip in order to
work with the Mini-Monitor software.

The RS232 converter has a male 9-pin D connector on the RS232 side.
Generally, the distance from the Mini-Monitor to the boiler controller
is substantial, so we used a CAT-5/6 patch cord to make the connection.
To convert the RJ45 connector on the patch cord to the 9-pin connector
on the RS232 converter, we used a `Cables To Go 02941 RJ45/DB9 Female
Modular Adapter available from
Amazon <http://www.amazon.com/Cables-02941-Female-Modular-Adapter/dp/B000067RSY/>`_.
Only 3 pins on the RS232 9-pin connector are used, and the wiring
connections are shown below, going from the DB-9 connector on the
USB-to-RS232 converter, to the RJ45/DB9 Adapter, to the CAT-5/6 cable,
and finally to the AERCO BMS II Boiler Manager screw terminals. Note
that the wire colors for the RJ45/DB9 Adapter are specific to this
particular model of adapter (the Cables to Go model mentioned above).

::

    DB-9 Pin 3, Transmit from Pi -- RJ45/DB9 Adapter Orange -- CAT-5/6 Orange -- AERCO RXD Terminal
    DB-9 Pin 2, Receive to Pi -- RJ45/DB9 Adapter Yellow -- CAT-5/6 Green -- AERCO TXD Terminal
    DB-9 Pin 5, Signal Ground -- RJ45/DB9 Adapter Blue wire -- Cat-5/6 White-Orange -- AERCO 232 ISO GND Terminal

Here is a picture of the CAT-5/6 patch cable with the RJ45/DB9 Adapter
at one end and bare wires at the other ready for attachment to the AERCO
BMS II screw terminals.

.. image:: /_static/aerco_cable.jpg

For more information of the RS232 interface of the AERCO BMS II Boiler
manager, see the `BMS II
Manual <https://github.com/alanmitchell/mini-monitor/wiki/develop/manuals/aerco_bmsII_manual.pdf>`_. The default
RS232 settings for the BMS II are appropriate for use with the
Mini-Monitor.

1-Wire Sensor Interface, Parts CV3 and PS2
------------------------------------------

1-Wire DS18B20 Temperature sensors and `Analysis North 1-Wire Motor
sensors <http://analysisnorth.com>`_ can be read by the Mini-Monitor.
The Analysis North Motor Sensor attaches via high-temperature Velcro to
an AC motor, an AC valve, or most any device that emits an AC
electromagnetic field, and detects when the device turns On and Off. For
more information on the 1-Wire Bus System, see this `Wikipedia
Article <https://en.wikipedia.org/wiki/1-Wire>`_. To communicate with
the 1-wire sensor network, a USB-to-1-wire converter or "Master" is
required. Three different types were tried, and the most suitable and
reliable for this application was a converter based on the `HA7S - ASCII
TTL 1-Wire Host Adapter
SIP <http://www.embeddeddatasystems.com/HA7S--ASCII-TTL-1-Wire-Host-Adapter-SIP_p_23.html>`_.
The schematic and assembly of this converter is :ref:`documented on this
page <one-wire-masster-interface-circuit>`.

If the sensor network includes any Analysis North 1-wire motor sensors,
a power supply, PS2, must be connected to the CV3 USB-to-1-wire
converter. This power supply supplies power to the 1-wire sensor
network; the DS18B20 temperature sensors do not need the power supply,
but the Motor Sensors do. Note, for noise isolation, this power supply
**must** be separate from the supply used by the Raspberry Pi and
Cellular Router. The power supply outputs 5 VDC with at least 100 mA of
current supplying capacity, the power connector is a 2.1mm x 5.5mm
barrel jack (center positive), and a suitable supply is the `CUI
EPS050100-P5RP <http://www.digikey.com/product-detail/en/EPS050100-P5RP/T1038-P5RP-ND/2004025>`_.
However, almost any *regulated* 5 VDC supply with correct connector
should work.

The 1-wire sensors are connected in a daisy chain configuration using
CAT-5/6 patch cords and RJ45 splitters to form the network. See the
:ref:`1-wire-sensors-and-cabling` page for more important detail on the
sensors and their interconnection.

SDR Radio for Utility Meter Reading, Part CV4
---------------------------------------------

The Mini-Monitor is able to read Utility meters (natural gas, electric,
and water) that utilize the Itron ERT radio transmission format to
broadcast their readings in the 900 MHz ISM band to meter readers
driving through the neighborhood. The hardware required to receive these
transmissions is shown as CV4 in the System Diagram at the top of this
document. This part is a Software Defined Radio utilizing a RTL2832U
radio chip and a R820T2 Tuner chip, interfaced through the Mini-Monitor
USB port. Examples of this radio device that have been tested with the
Mini-Monitor are:

*  `RTL-SDR Blog Software DefinedcRadio <https://www.amazon.com/RTL-SDR-Blog-RTL2832U-Software-Telescopic/dp/B011HVUEME/>`_
*  `NooElec NESCR Minic2+ <https://www.amazon.com/NooElec-NESDR-Mini-Receiver-RTL2832U/dp/B00VZ1AWQA/>`_
*  `NooElec NESCR SMArt PremiumcRTL-SDR <https://www.amazon.com/NooElec-NESDR-SMArt-Enclosure-R820T2-Based/dp/B01GDN1T4S/>`_

To enable and configure the recording of utility meter readings, certain
settings must be made in the :ref:`Mini-Monitor Settings file <software>`.

Surge Protector
---------------

For further protection from power quality issues, the two power
supplies, PS1 and PS2, are plugged into a surge protector, typically
mounted adjacent to the Mini-Monitor enclosure. Unless a third power
supply is needed due to not sharing PS1 between the Raspberry Pi and the
Dovado cellular router, a two outlet surge protector is sufficient. We
use the `Tripp Lite ISOBAR2-6 available from
Amazon <http://www.amazon.com/Tripp-Lite-ISOBAR2-6-Outlet-Protector/dp/B0000510Z9/>`_.
This model lineup also has a four outlet version, if needed.

Mini-Monitor Enclosure, Component Mounting, Wiring Channel
----------------------------------------------------------

Other than the power supplies and the surge protector, the Mini-Monitor
components are mounted inside an enclosure with a hinged door. The
enclosure we use is the `Arlington EB1212-1 available from
Amazon <http://www.amazon.com/Arlington-EB1212-1-Electronic-Equipment-Non-Metallic/dp/B00AAU5D6Q/>`_.
Some of the components comes with mounting tape (J1) or a hook and loop
fastening pad (Dovado Tiny). For other components we have found `3M
Command Brand Medium Picture Hanging
Strips <http://www.amazon.com/Command-Medium-Picture-Hanging-Strips-6-Strip/dp/B000M3YGOQ/>`_
to work well for attachment.

Wiring between components can be organized and provided strain relief
through use of comb-type wiring duct. Economical sources can be found on
Ebay by searching for "Wiring Duct".
