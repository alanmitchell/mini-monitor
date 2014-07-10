#!/usr/bin/python
"""Starts up the cellular internet connection.
** Must be run as root user.
"""

import subprocess, time, os

# kill wvdial if it is running, as this script is used to restart the network
# in some situations.

subprocess.call('/usr/bin/killall wvdial', shell=True)

# wait for up to 10 seconds for this to complete
for i in range(10):
    try:
        subprocess.check_output('ps aux | grep wvdial | grep -v grep', shell=True)
        time.sleep(1)
    except:
        # the check_output command will error if grep finds nothing, meaning
        # wvdial was successfully killed.
        break

# check and see if mode_switch has occurred and the gsmmodem device has been
# created.  Often on a cold boot, mode_switch does not occur so needs to be 
# accomplished here.

if not os.path.exists('/dev/gsmmodem'):
    # retriggering the udev facility will cause modeswitch to run and set
    # up the /dev/gsmmodem symbolic link.
    subprocess.call('/sbin/udevadm trigger', shell=True)

    # wait for up to 20 seconds for the sym link to appear
    for i in range(20):
        if os.path.exists('/dev/gsmmodem'):
            break
        time.sleep(1)
    
# start wvdial in the background.  Check to see if this is the Huawei E173
# and use a different init string for that modem.
if '12d1:1436' in subprocess.check_output('/usr/bin/lsusb'):
    subprocess.call('/usr/bin/wvdial E173 &', shell=True)
else:
    subprocess.call('/usr/bin/wvdial &', shell=True)

# wait for wvdial to connect
time.sleep(30)
