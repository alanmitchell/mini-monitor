.. _software:

Software
========

This section of the Wiki explains how to install and configure the
Mini-Monitor software on a Raspberry Pi computer. There are three steps
to install and configure the software.

1. Download, unzip, and write the Image file containing the Mini-Monitor
   software onto an SD card.
2. Insert the SD card into a PC and edit the Settings file to configure
   the Mini-Monitor for your application.
3. Boot the Raspberry Pi with the SD card, log on, and upgrade the
   Mini-Monitor software to the newest release. Reboot to begin using
   the newest software.

Each of these three steps is described in more detail in the following
sections.

Download and Install Mini-Monitor SD Card Image
-----------------------------------------------

The Raspberry Pi uses an SD card as a solid-state drive for storage of
the operating system and all programs and user data. We have made a
complete image of the SD card containing the Raspbian Linux Operating
System and the entire Mini-Monitor software application. You can
download a zipped version of this image from the link below. The file is
about 1 GB in size so will take some time to download.

`Mini-Monitor SD Card Image (1.0 GB) <http://analysisnorth.com/mini_monitor/mini_monitor_sd_2017-05-02.zip>`_

First unzip the file to extract a '.img' file, which is the SD card image. Use the `instructions
here <https://www.raspberrypi.org/documentation/installation/installing-images/>`_
under the "WRITING AN IMAGE TO THE SD CARD" heading to write the image
to an 8 GB micro-SD card, if you are using a Raspberry Pi B+, 2 or 3; or
a standard 8 GB SD card for the older model B Pi.

Setup Internet Access
---------------------

The SD card has a partition that is readable on a Windows PC, Mac, or
Linux computer. On a Windows PC it will show up as a drive labeled
"boot". There are some configuration files on this partition that need
attention before running the Mini-Monitor.

Although these files are useable on a Windows PC, they are text files
that use the line-ending format used on Linux computers. It is important
to preserve that type of line-ending when editing the files. The
standard Notepad program that comes with the Windows Operating System
does *not* preserve Linux line endings. Most text editors used for
programming *do* preserve line endings, such as EditPlus or Notepad++.
You need to use one of these editors when editing the files described in
this section and the next.

The first issue to address is setting up Internet Access. In the
``pi_logger/`` directory on the SD card is a shell script file called
``start_inet``. This file is executed when the Pi starts up, and its
purpose is to start Internet access for methods of Internet access that
do not start automatically. If the Internet access is being provided via
an Ethernet connection to the Pi, no special Internet startup command
are needed; in this case ``start_inet`` should contain no commands. A
blank script file is available at
``pi_logger/inet_scripts/start_inet.NULL``, and this file can be copied
onto ``pi_logger/start_inet``. This is also the appropriate set up for
an Ethernet connection to a Cellular Router, See Option 2 in the :ref:`hardware` document.

The same blank ``start_inet`` file can be used when Internet Access is
being provided via WiFi (either the built-in WiFi adapter in the
Raspberry Pi 3 or a WiFi USB dongle). This is because the Raspberry Pi
will take care of establishing the WiFi Internet connection without a
special startup script. For more details on setting up a WiFi connection
for the Raspberry Pi, `click here <https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md>`_.

The common scenario where a non-blank ``start_inet`` is required is when
a Cellular Modem is directly connected to the Raspberry Pi via a USB
port; this is Option 1 in the :ref:`hardware` document. In this
scenario, the ``start_inet`` script runs the ``UMTSkeeper`` command,
which establishes and maintains an Internet connection through the
Cellular Modem. Each Cellular Modem requires different configuration
parameters to be used by the UMTSkeeper script. There are a few
different ``start_inet`` scripts in the ``pi_logger/inet_scripts/``
directory for a few different types of Cellular modems. For the GCI
network in Alaska, we recommend the Sierra Wireless 313U modem, and
scripts are available in ``pi_logger/inet_scripts/`` for that modem.
Copy the appropriate script on to ``pi_logger/start_inet``. If no script
is available for your cell modem, you will need to learn about
configuration of the UMTSkeeper program; see `this page <http://mintakaconciencia.net/squares/umtskeeper/>`_, and create an
appropriate ``start_inet`` script.

Configure Settings File for your Application
--------------------------------------------

The next step is to edit the special Mini-Monitor Settings file on the
SD card to configure the software for your application. The settings
file is found at ``pi_logger/settings.py``. (When actually running on
the Pi, the path is ``/boot/pi_logger/settings.py``.)

Open this file in a text editor; see the discussion in the prior section
regarding the use of a Text Editor that preserves Linux line endings.
This file is essentially a `Python <https://www.python.org/>`_ code
file, but the only types of statements in the file are comments (any
text appearing after a "#" symbol) and variable assignment statements,
like:

.. code:: python

    LOGGER_ID = 'test'

The rest of this section will explain they key variables that can be
altered in this file. Excerpts from the file will be shown followed by
an explanation of setting. After modifying values in the file, simply
save it back to the SD card.

.. code:: python

    # The unique ID of this particular logger, which will be prepended to
    # sensor IDs.
    LOGGER_ID = 'test'

Each Mini-Monitor needs to be assigned an ID name that is unique across
all of the Mini-Monitors posting data to a particular BMON web site. The
ID should be kept to 13 characters or less, and only use letters and
numbers (no spaces). An example is 'Okla511', which was used for a
building at 511 Oklahoma Street. As shown in the example above, the ID
string must be enclosed in single or double quotes.

.. code:: python

    # The intervals for reading sensors and for logging readings
    READ_INTERVAL = 5     # seconds between readings
    LOG_INTERVAL = 10*60  # seconds between logging data

The ``READ_INTERVAL`` setting controls how often the Mini-Monitor reads
the sensors attached to it. The value is expressed in seconds, and in
general it should be a value of 5 seconds or longer. The
``LOG_INTERVAL`` expressed in seconds determines how often the sensor
readings are summarized and posted to the BMON server. As you can see in
the example above, a math expression can be used, such as ``10 * 60``. If
``READ_INTERVAL`` is set to 5 seconds and the ``LOG_INTERVAL`` is set to
10\*60 or 10 minutes, sensors will be read 120 times before their data
is posted to the BMON server. For analog sensors or readings, for
example temperature, the 120 readings are averaged together before being
posted to the BMON server. A post is timestamped in middle of the 10
minute interval, since the posted value represents conditions occurring
throughout the interval.

For sensors or readings that are state values, such as On/Off readings
or perhaps a Fault Code, every change of state that occurs in the 10
minute interval is posted as a separate reading value, appropriately
timestamped. The last state recorded in the interval is also posted,
even if no change occurred in the interval.

Note that these settings do *not* apply to separate processes that post
sensor data directly to the Mini-Monitor MQTT broker; the settings apply
only to the Sensor Reader Classes described in a following section. As
an example, the Utility Meter Reader script is a separate process that
posts directly to the MQTT broker; it has a separate interval setting
found near the bottom of the Settings file and described later in this
document.

Settings related to Posting to a BMON Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # Set following to True to enable posting to a BMON server
    ENABLE_BMON_POST = True

    # URL to post readings to, and required storage key
    # An example BMON URL is "https://bms.ahfc.us"
    # The Store Key can be any string with no spaces
    POST_URL = '[BMON URL goes here]/readingdb/reading/store/'
    POST_STORE_KEY = 'Store Key Goes Here'

``ENABLE_BMON_POST`` should be set to ``True`` to have the Mini-Monitor
post data to a BMON server. The ``POST_URL`` is the Internet URL where
the Mini-Monitor will post its data. For a BMON web-based sensor system,
a sample URL is ``https://bms.ahfc.us/readingdb/reading/store/``. The
particular BMON system you are posting to has a secret storage key,
which should be entered as the ``POST_STORE_KEY`` setting.

Sensor Reader Classes
^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # A list of sensor reader classes goes here
    READERS = [
    'ha7s.HA7Sreader',             # 1-Wire Sensors
    'sage_boiler.Sage21Reader',    # Burnham Alpine Boilers w/ Sage 2.1 controller
    #'aerco_boiler.BMS2reader',    # AERCO BMS II Boiler Mangager
    #'dg700.DG700reader',          # Energy Conservatory DG-700 Pressure Gauge
    #'labjack.LabjackTempReader',  # Thermistors connected to Labjack U3
    #'sensaphone.SensaphoneReader',   # Reads Node sensors from Sensaphone IMS 4000
    'sys_info.SysInfo',            # System uptime, CPU temperature, software version
    ]

The ``READERS`` setting holds a list of sensor reading code segments
that are needed for your application. If you want to use a particular
sensor reader, remove the '#' symbol from the beginning of the line. To
disable a particular sensor reader type, enter a '#' at the beginning of
the line. In the example above, three sensor readers are enabled:

*  The reader for 1-Wire sensors connected to the Mini-Monitor.
*  The reader that will collect data from a Burnham Alpine Boiler using
   the Sage 2.1 controller.
*  A reader that will report general system information including the
   amount of time the system has operated since the last reboot, the
   temperature of the CPU, and the Mini-Monitor software version.

Do not change anything else in this section other than adding or
removing '#' symbols from the beginning of reader lines.

More detail is provided on each reader type in the :ref:`available-sensor-readers` document. That document explains what values are read and
reported by the various readers.

Settings related to Mini-Monitor Health
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # Number of days of uptime between forced reboots.  Set to 0 to never reboot.
    REBOOT_DAYS = 2

    # Reboots if Error Count is too high
    CHECK_ERROR_CT = False

    # Reboots if Last Post was too long ago
    CHECK_LAST_POST = False

The Mini-Monitor can be configured to automatically reboot itself every
so often, which can add to the stability of the system when unforeseen
problems are occurring. The value of ``REBOOT_DAYS`` is expressed in
days, and we have typically chosen to reboot every two days. If the
setting is set to 0, the Mini-Monitor will never intentionally reboot.

If ``CHECK_ERROR_CT`` is set to True, the Mini-Monitor will reboot if
the number of errors occurring in the application are too high. If
``CHECK_LAST_POST`` is True, a reboot will occur if the Mini-Monitor is
not successfully posting readings to the BMON server.

Settings related to Logging Errors, Warnings, and Operational Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # This controls what messages will actually get logged in the system log
    # 'Logging' here does *not* refer to sensor logging; this is error and debug
    # logging.
    # Levels in order from least to greatest severity are:  DEBUG, INFO, WARNING, 
    # ERROR, CRITICAL
    LOG_LEVEL = logging.INFO

This setting controls how Error and Debug logging operates in the
Mini-Monitor. The setting is not related to *sensor* logging, instead,
is relates to logging of how the program code is operating. The
``LOG_LEVEL`` setting determines how many events are recorded into the
log file. We normally run this at the ``logging.INFO`` level, but when
debugging a problem, more information will be logged with the
``logging.DEBUG`` value. The main log file is located on the Raspberry
Pi at ``/var/log/pi_log.log``. Other log files associated with the
Mini-Monitor are: ``/var/log/pi_cron.log``,
``/var/log/mqtt_to_bmon.log``, ``/var/log/meter_reader.log``, and
``/var/log/mosquitto.log``. All of these files, except ``mosquitto.log``
are affected by the ``LOG_LEVEL`` setting.

Settings related to Recording Data from a Sensaphone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # If you are using the sensaphone.SensaphoneReader reader, then you need
    # to set the IP address of the Host Sensaphone unit below
    SENSAPHONE_HOST_IP = '10.30.5.77'

This final setting is only necessary if you are using the
SensaphoneReader class. The IMS-4000 host IP address should be entered
in this section, using single quotes. Ensure that the device has access
to the network where the IP address is located.

Settings related to Recording Transmissions from Utility Meters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    # Set to True to enable the meter reader
    ENABLE_METER_READER = False

    # A Python list of the Meter IDs you wish to capture and post.
    METER_IDS = [1234, 6523, 1894]

    # The minimum number of minutes between postings. If you set
    # this too low, the resolution of the posted meter reading delta
    # will be low.
    METER_POST_INTERVAL = 30  # minutes

These settings are for the script that can receive meter reading
transmissions from certain Utility meters. See the :ref:`hardware` document for the necessary Mini-Monitor hardware. Also, further
discussion of the values posted by this script is in the :ref:`available-sensor-readers` document.

The ``ENABLE_METER_READER`` setting must be True to enable reading of
utility meter transmissions. ``METER_IDS`` is a Python list containing
the Meter IDs of the meters you wish to record. You can generally find
the Meter ID number on the meter nameplate, as shown in this picture:

.. image:: /_static/meter_id.jpg

``METER_POST_INTERVAL`` is the minimum number of minutes between meter
readings that are used to create a recorded/posted value. As explained
in the :ref:`available-sensor-readers` document, the script posts the amount of
the change in the utility meter value, so if this
``METER_POST_INTERVAL`` is too short, a low resolution change value will
be reported.

Upgrade Mini-Monitor Software to Newest Release
-----------------------------------------------

Once you have updated the Settings file on the SD card, the next step is
to start the Raspberry Pi and upgrade the Mini-Monitor software to the
newest version. Insert the SD card into the Raspberry Pi, connect an
Ethernet cable with Internet access, and apply power. Then, log onto the
Pi either through use of a console cable or an SSH connection (see
Raspberry Pi documentation for details on these methods). The log on
credentials are:

::

    mini-monitor login:  pi
    Password:  minimonitor

Change into the main software directory and update the software using a
Git source control pull command by using these commands:

::

    cd pi_logger
    git pull

If you would like to change the log-in password, use the ``passwd``
command. Reboot the logger to utilize the new software:

::

    sudo reboot

In the future if you need to update the Mini-Monitor software, this same
process should be repeated. Also, for a new update, you should inspect
the ``/home/pi/pi_logger/system_files/settings_template.py`` sample
Settings file to see if any new setting variables have been added, which
could require an update of your actual Settings file, as discussed in
the prior section.