.. _configuring-the-dovado-tiny-cellular-router:

Configuring the Dovado Tiny Cellular Router
===========================================

#. Log onto the router as indicated in the Dovado Quick Wizard Guide
   that came with the router.
#. The Wizard will pop up. Complete the selections, with the following
   notes.
  	On the WLAN (Wireless LAN) page, Disable the Wireless LAN.
  	On the Internet Page, if you are using the GCI cellular network, type
	in ``web.gci`` as the Access Point Name; leave the PIN Code blank. If
	using a different mobile wireless provider, enter their APN.
#. The Router will restart.
#. Log back into the router with the new password.
#. On the Home page screen, the Router firmware will be listed. Make
   sure the firmware is appropriate for the USB cellular modem you are
   using. For the combinations of Cellular Modems and Router Firmwares
   that have worked for us, please see the Part CM1, USB Cell Modem
   section of :ref:`hardware` page. If the router firmware is not
   appropriate, go to the `Dovado Firmware Page <http://www.dovado.com/en/support/firmware>`_ to download
   firmware and install according to the instructions there.
#. After logging back into the router, select ``Internet`` from the
   sidebar and ``Connection Tracker`` from the top menu bar. Check the
   box to Enable the Connection Tracker. The Connection Tracker
   periodically checks the Internet connection and takes remedial action
   to restore it, if necessary. Cycling power to the cell modem USB port
   is used as a last resort. It is very important to enable this
   feature.
#. For ``IP Address 1`` type in ``8.8.8.8`` (a Google DNS server)
#. For ``IP Address 2`` type in ``4.2.2.2`` (a Level-3 DNS server)
#. For the ``Interval`` type in ``15`` minutes
#. For ``Failure Handling`` select ``Redial and Restart``
#. Click the ``Save Settings`` button
#. Select ``Modem`` from the sidebar and ``Modem Settings`` from the top
   bar. Verify that the Access Point Name setting from the wizard is
   shown. If not, uncheck ``My service does not require APN`` and fill
   in the Access Point Name. Click the ``Save Settings`` button.
#. Select ``Restart`` from the sidebar and click the ``Restart`` button.
#. Note that the router will often take 2 to 3 minutes to connect to the
   Internet (solid light on modem) even though the web interface to the
   router is available within about one minute.
#. The Setup process is complete.
