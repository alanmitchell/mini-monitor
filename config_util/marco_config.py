'''This is a small GUI utility that helps to configure the Mini-Monitor
by modifying values in the settings.py file and by setting up WiFi
Internet access if requested.  

This special configuration utility is built for Marco Castillo's Enstar 
project.  It only configures the Site ID, the Internet, and sets the Meter
IDs to read.  All the other configuration for the project is assumed to be
in the settings file already.

Normally, this setup utility is compiled into a Windows and Mac executable
and put on the /boot partition of the Mini-Monitor SD card.
PyInstaller, http://www.pyinstaller.org/documentation.html is used compile
the Python script into an executable file.  To create a Windows executable,
PyInstaller must be run on a Windows machine.  To create a Mac executable,
it must be run on a Mac machine.

Here is the syntax to create a one-file Windows executable:

    pyinstaller -F settings_editor.py

which creates 'settings_editor.exe' (Windows) in the subdirectory 'dist'.
This is usually renamed to settings_editor_win.exe and put on the '/boot'
partition of the Mini-Monitor SD card.  If pyinstaller is run on a Mac,
'settings_editor' is created, which is typically renamed to 'settings_editor_mac'
and placed on the boot partition.
'''

from tkinter import *
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import io
import os
import sys
import re
import setup_utils

def store_settings():
    # Stores the setting info from the GUI into
    # the Mini-Monitor settings file.  Returns the value 0
    # if Success, -1 if an error.

    try:

        # gather the data from the interface
        logger_id = site_entry.get().replace(' ', '')
        meter_ids = meter_ids_entry.get()
        internet_type = inet_type.get()
        w_ssid = wifi_ssid_entry.get()
        w_pass = wifi_pass_entry.get()

        # Do a few input checks
        if len(logger_id.strip())==0:
            tkinter.messagebox.showerror('No Site Name', 'You must enter a Site Name.')
            return -1

        if internet_type=='wifi':
            if len(w_ssid.strip())==0:
                tkinter.messagebox.showerror('No WiFi Name', 'You must enter a WiFi Network Name.')
                return -1

        substitutions = [
            (r'LOGGER_ID\s*=', "LOGGER_ID = '%s'" % logger_id)
        ]

        substitutions += [
            (r'ENABLE_METER_READER\s*=', 'ENABLE_METER_READER = True'),
            (r'METER_IDS\s*=', 'METER_IDS = [%s]' % meter_ids),
        ]

        # read settings file and perform the substitutions.
        # First need to identify the directory where this program
        # is located.  The method used to find it depends on whether
        # this is running as a script or as a pyinstaller frozen
        # executable.  See https://pythonhosted.org/PyInstaller/runtime-information.html.
        if getattr(sys, 'frozen', False):
            THIS_DIR = os.path.dirname(sys.executable)
        else:
            THIS_DIR = os.path.dirname(os.path.abspath(__file__))

        settings_fn = os.path.join(THIS_DIR, 'pi_logger/settings.py')
        with open(settings_fn) as f:
            file_contents = f.read()
        file_contents = setup_utils.replace_line(file_contents, substitutions)

        # Write the revised settings file.
        with io.open(settings_fn, 'w', newline='\n') as f:
            f.write(str(file_contents))

        # Make the proper wpa_supplicant.conf file.
        if internet_type=='wifi':
            file_contents = setup_utils.wpa_sup_file(ssid=w_ssid, psk=w_pass)
        else:
            file_contents = setup_utils.wpa_sup_file()
        sup_fn = os.path.join(THIS_DIR, 'wpa_supplicant.conf')
        with io.open(sup_fn, 'w', newline='\n') as f:
            f.write(str(file_contents))

        msg = 'The Settings were Successfully Stored!  You can now close the application or modify settings and Store again.'
        tkinter.messagebox.showinfo('Success', msg)
        return 0

    except Exception as e:
        tkinter.messagebox.showerror('Error Occurred', 'An Error occurred while attempting to store settings:\n%s' % str(e))
        return -1

def inet_visibility():
    """Manage visibility of Internet Type widgets.
    """
    wifi_frame.grid_remove()
    i_type = inet_type.get()
    if i_type=='ethernet':
        pass
    elif i_type=='wifi':
        wifi_frame.grid()

root = Tk()
root.title('Marco Enstar Project Configuration')

# Increase font sizes a bit
default_font = tkinter.font.nametofont("TkDefaultFont")
default_font.configure(size=11)
text_font = tkinter.font.nametofont("TkTextFont")
text_font.configure(size=11)

# Main Frame to hold all widgets
mainframe = tkinter.ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky='EWNS')
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Site ID entry
tkinter.ttk.Label(mainframe, text='Enter the ID for this Home (20 character max, no spaces):').grid(
    column=0, row=0, sticky=W)
site_entry = tkinter.ttk.Entry(mainframe, width=20)
site_entry.grid(column=0, row=1, sticky=W)

# Gas Meter Reader related
meter_ids_label = tkinter.ttk.Label(mainframe, text='Enter the Gas Meter ID:')
meter_ids_label.grid(column=0, row=4, sticky=W)
meter_ids_entry = tkinter.ttk.Entry(mainframe, width=50)
meter_ids_entry.grid(column=0, row=5, sticky=W)

#---- Internet Access
inet_frame = tkinter.ttk.LabelFrame(mainframe, text='Select Internet Access Type')
inet_frame.grid(column=0, row=6, sticky=W)
inet_type = StringVar()
tkinter.ttk.Radiobutton(inet_frame, text='WiFi', variable=inet_type, value='wifi', command=inet_visibility).grid(column=0, row=0)
tkinter.ttk.Radiobutton(inet_frame, text='Ethernet', variable=inet_type, value='ethernet', command=inet_visibility).grid(column=1, row=0)
inet_type.set('wifi')
for child in inet_frame.winfo_children():
    child.grid_configure(padx=10, pady=5)

# WiFi credentials
wifi_frame = tkinter.ttk.Frame(mainframe)
wifi_frame.grid(column=0, row=7, sticky=W)
tkinter.ttk.Label(wifi_frame, text='WiFi Network Name (SSID):').grid(column=0, row=0, sticky=E)
wifi_ssid_entry = tkinter.ttk.Entry(wifi_frame, width=30)
wifi_ssid_entry.grid(column=1, row=0)
tkinter.ttk.Label(wifi_frame, text='WiFi Password (leave blank if Open network):').grid(column=0, row=1, sticky=E)
wifi_pass_entry = tkinter.ttk.Entry(wifi_frame, width=30)
wifi_pass_entry.grid(column=1, row=1, sticky=W)
for child in wifi_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

tkinter.ttk.Separator(mainframe, orient=HORIZONTAL).grid(column=0, row=11, sticky='EW')
tkinter.ttk.Button(mainframe, text='Store these Configuration Settings', command=store_settings).grid(column = 0, row=12)

# Add some padding to all widgets in mainframe
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# run routines to get initial visibility correct
inet_visibility()

root.mainloop()
