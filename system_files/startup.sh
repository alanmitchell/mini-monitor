#!/bin/sh
#
# This script is executed by /etc/rc.local at bootup.  The contents of
# /etc/rc.local should be:

# --------------------
# #!/bin/sh
# set +e
# /home/pi/pi_logger/system_files/startup.sh
#
# # Run the site-specific startup file.  Add any other commands to this
# # rc.local.site file, and they will execute at boot up.  Make sure 
# # rc.local.site is executable.
# /etc/rc.local.site
#
# exit 0
# --------------------

# From here on, do NOT exit the script if any errors occur
# (this may already be the case, since I removed the "-e" option from
# the shebang line above).
set +e

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

# Below I create a "forcefsck" file in /, which
# causes fsck to run on every boot (which then removes the forcefsck file). I 
# also have set FSCKFIX=yes in the/etc/default/rcS file, which will cause fsck
# to attempt to repair even serious errors; a "no" causes fsck to repair minor
# errors but requires human intervention for more serious errors.
touch /forcefsck

# If a Cell Modem is being used, start it up.
if /home/pi/pi_logger/scripts/test_setting.py USE_CELL_MODEM
then
	/home/pi/pi_logger/scripts/start_cell_modem &
fi

# The Mosquitto MQTT broker is started as a service, see: 
# /etc/systemd/system/mosquitto.service

# If requested in the mini-monitor settins file, start the service that listens 
# for sensor readings from the MQTT broker and then posts those to a BMON server.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_BMON_POST
then
	/home/pi/pi_logger/scripts/run_mqtt_to_bmon &
fi

# Always start up pi_logger because it makes a status post to api.analysisnorth.com
/home/pi/pi_logger/scripts/run_pi_logger &

# Start the programs for Utility Meter reading, if requested in the settings
# file.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_METER_READER
then
	/home/pi/pi_logger/scripts/run_meter_reader &
fi

# Start the programs for reading 433 MHz wireless sensors, if requested in
# the settings file.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_RTL433_READER
then
	/home/pi/pi_logger/scripts/run_rtl433_reader &
fi

# Start the program for reading the PZEM-016 power sensor, if requested in
# the settings file.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_POWER_MONITOR
then
	/home/pi/pi_logger/scripts/run_power_monitor &
fi

# Start the multi-channel pulse counter script, if requested in
# the settings file.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_PULSE_COUNTER_MULTI_CH
then
	/home/pi/pi-energy-sensors/run_pulse_counter_multi_ch &
fi

# Start the BTU meter script, if requested in the settings file.
if /home/pi/pi_logger/scripts/test_setting.py ENABLE_BTU_METER
then
	/home/pi/pi-energy-sensors/run_btu_meter &
fi

# Turn off he HDMI interface to save power
/usr/bin/tvservice -o
