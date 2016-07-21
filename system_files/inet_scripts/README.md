## Notes about Internet Start Up Scripts

There is a script named `/boot/pi_logger/start_inet` on the Raspberry Pi,
which is used to start the Internet if it does not automatically start.
This is typically used for starting a Cell Modem.  The scripts in this repo
directory can be used for that `start_inet` script.  Copy the appropriate
one from here to the above location on the Raspberry Pi.

For convenience, these scripts have been duplicated into the
`/boot/pi_logger/inet_scripts` directory so that they are accessible
when the Pi SD card is plugged into a Windows PC.  Note that if any
script changes or new scripts are added to this Git repo, they must
be manually duplicated again to the `/boot/pi_logger/inet_scripts`
convenience directory.
