.. _developers:

Developers
===========


This section of the Wiki is aimed at developers who wish to better
understand and perhaps modify the Mini-Monitor software. The code is
thoroughly commented, but the documents described below are meant to
provide higher level documentation for the application. It is
recommended that the :ref:`Software Introduction <Software>` document be
read as a prerequisite to this document.

Mini-Monitor is a Python 2 application and is currently running with
Python 2.7.9 on the Raspberry Pi running a Raspbian Jessie Light Linux
distribution, March 2017 version. On the Raspberry Pi, the Python code
for the application is found in the ``pi`` user's directory space in the
folder ``/home/pi/pi_logger``. References to file paths in the following
text will all be relative to that directory.

Overall Structure of the Application
------------------------------------

Starting with version 1.7, the Mini-Monitor software is designed to use
an `MQTT Broker <http://mqtt.org/>`_ to manage the transport of sensor
readings from software that acquires the readings to software that
consumes the readings, for example, software that posts the readings to
a BMON server. The specific MQTT broker that is used and hosted on the
Mini-Monitor is `Mosquitto <https://mosquitto.org/>`_. The broker runs
as a daemon on the Raspberry Pi and is started via the systemd script
``/etc/systemd/system/mosquitto.service``.

As of version 1.7, there are two different processes that acquire sensor
readings and publish them to the MQTT broker:

*  ``pi_logger.py``: This script instantiates "Readers" that are enabled
   in the :ref:`settings` file (more details in the next section), and these readers periodically read
   their associated sensors. After passage of a logging interval of time
   (as entered in the Settings file), ``pi_logger.py`` publishes reading
   summaries to the MQTT broker (average values for analog sensors, or
   state changes for sensors that determine the state of a device).
*  ``meter_reader.py``: The Mini-Monitor has the ability to listen to
   meter reading radio broadcasts from utility meters. The utility meter
   is not "polled" by the Mini-Monitor but instead waits for readings to
   arrive. So, the ``pi_logger.py`` style of sensor reading did not
   apply. Instead, a separate script is available that listens for these
   readings and publishes rates of change of the cumulative meter value
   to the MQTT broker.

Both of these sensor reading scripts are started by the standard
``rc.local`` script that the Raspberry Pi runs at the end of its boot up
process. In order to include the ``rc.local`` script in the Mini-Monitor
source code, a symlink is created from the standard ``/etc/rc.local``
file to an ``rc.local`` file located in the Mini-Monitor software folder
at ``system_files/rc.local``. It is valuable to look at this file for
other details on the Mini-Monitor start-up process.

``pi_logger.py`` is only started if at least one Reader file is enabled
in the Settings file. ``meter_reader.py`` is only started if the Utility
Meter reader feature is enabled in the Settings file.

As of Version 1.7, there is only one possible consumer of sensor
readings published to the MQTT broker: the ``mqtt_to_bmon.py`` script,
which receives sensor readings and posts them to a BMON server on the
Internet. Enabling and configuring that script occurs in the Settings
file. If enabled, it runs in a separate process from ``pi_logger.py``
and ``meter_reader.py``. In the future, a basic log-to-disk sensor
reading consumer is envisioned.

``mqtt_to_bmon.py`` subscribes to the ``readings/final/#`` topic on the
MQTT broker. All sensor readings published to that topic set will be
received by ``mqtt_to_bmon.py`` and posted to the BMON server.
``pi_logger.py`` publishes to the topic ``readings/final/pi_logger`` and
``meter_reader.py`` publishes to the topic
``readings/final/meter_reader``.

Reader Files
------------

The Mini-Monitor is designed so that is easy to mix different sensor
types and data sources in the data acquisition process. As mentioned in
the prior section, ``pi_logger.py`` utilizes Reader classes to read
different types of sensors. Each Reader class knows how to gather data
from a particular data source, e.g. a 1-wire sensor network or a
particular boiler type. The ``READERS`` setting in the :ref:`settings` file holds that
list of classes. The list items for the ``READERS`` setting are in the
format of ``<file>.<class name>``. All of these files are located in the
``readers`` directory of the application.

Each specific Reader class inherits from ``readers/base_reader.Reader``.
The specific Reader class only needs to implement a ``read()`` method.
The requirements for that ``read()`` method are described in the
``base_reader.Reader`` base class. Basically, the ``read()`` method
returns a list of sensor readings.

A number of equipment manuals are available that relate to the existing
Reader classes. These are listed and are accessible from the :ref:`relevant-manuals` page.

So, to add a new type of data source to the Mini-Monitor software, you
only need to write a new Reader class and put that class in the
``readers`` directory. Then, add the class to the ``READERS`` variable
found in the Settings file, described in the next section.

Alternatively, a separate script can be written, similar to
``meter_reader.py``, that can acquire sensor readings and directly
publish them to the MQTT broker.

Settings File
-------------

In the :ref:`software` document, the Settings file was described in detail.
This file controls the types of data sources the deployed Mini-Monitor
will collect data from and controls a number of other data collection
parameters. The Settings file that is used by the deployed Mini-Monitor
is found at ``/boot/pi_logger/settings.py``. This file is not in source
control because it contains a secret Store Key for the BMON system
receiving the data, and it as setting specific to the particular
application being deployed. There is a sample Settings file that is kept
in source control and is present at
``system_files/settings_template.py``.

If you add a new Reader class to the Mini-Monitor software, you should
add the ``<file>.<class>`` name to the ``READERS`` variable in both the
sample Settings file (``system_files/settings_template.py``) and the
operational Settings file for the Mini-Monitors you have deployed that
need to use the new Reader.

Cron Tasks
----------

The Mini-Monitor system has a Cron job that runs every 15 minutes and
executes the ``scripts/cron_15m.py`` script. This script performs a
number of health checks on the Mini-Monitor, records some some summary
information in the application log file, and performs a few other tasks
that should run in a process independent of the main Mini-Monitor
software.

Raspbian OS Configuration
-------------------------

Some configuration was done to the Raspbian operating system for use in
the Mini-Monitor. As a user of the Mini-Monitor, if you download the SD
card image according to instructions on the :ref:`Software` page, you **do
not** need to perform any of the following configuration changes. The SD
card image already includes all of these configuration changes. The
information in this section is meant for developers attempting to
understand or modify the Mini-Monitor system.

A number of Mini-Monitor start up tasks are performed in the standard
``/etc/rc.local`` file. In order to keep this file under source control
so that it can be updated with Mini-Monitor software updates, the
``/etc/rc.local`` file was symlinked to
``/home/pi/pi_logger/system_files/rc.local``. ``git pull`` updates to
the source code can also update that start up file.

A couple modifications were made to reduce the number write operations
to the SD card. This improves the life of the card and also reduces the
chance of file corruption, which can occur if power is removed from the
Mini-Monitor during a SD card write operation. Actual occurrences of
file corruption were experienced, motivating the following changes.

The Swap file was permanently removed using the following commands:

::

    sudo apt-get remove dphys-swapfile
    sudo rm /var/swap

This reduces writes to the SD Card (although it rarely if ever was used)
and it also frees up space on the SD card. More free space improves the
life of the card because the write-leveling that occurs with the SD card
has more storage to work with.

A number of directories on the Pi file system were mounted on a RAM disk
via the following lines in the ``/etc/fstab`` file.

::

    tmpfs  /tmp      tmpfs  defaults,noatime,nosuid,size=100m            0 0
    tmpfs  /var/tmp  tmpfs  defaults,noatime,nosuid,size=30m             0 0
    tmpfs  /var/log  tmpfs  defaults,noatime,nosuid,mode=0755,size=100m  0 0
    tmpfs  /var/run  tmpfs  defaults,noatime,nosuid,mode=0755,size=2m    0 0

These directories, particularly the ``/var/log`` directory experience
numerous write operations, and mounting these on a RAM disk eliminates
the SD wear and file corruption chance from those writes.
