#!/usr/bin/python
"""Starts up the cellular internet connection.
** Must be run as root user.
"""

import subprocess, time

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
    
# start wvdial in the background.  
subprocess.call('/usr/bin/wvdial &', shell=True)

# wait for wvdial to connect but no longer than 30 seconds
tstart = time.time()
while time.time() - tstart < 30:
    try:
        subprocess.check_output(['/usr/bin/nslookup', 'google.com'])
        break
    except:
        # if nslookup is unsuccessful, it throws an error
        pass