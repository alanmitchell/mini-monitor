'''This is a small GUI utility that helps to configure the Mini-Monitor
to use it as an Power Outage monitor.  This script modifies
values in the settings.py file and sets up Internet Access

Normally, this setup utility is compiled into a Windows and/or Mac executable
and put on the /boot partition of the Mini-Monitor SD card.
PyInstaller, http://www.pyinstaller.org/documentation.html is used compile
the Python script into an executable file.  To create a Windows executable,
PyInstaller must be run on a Windows machine.  To create a Mac executable,
it must be run on a Mac machine.

Here is the syntax to create a one-file Windows executable:

    pyinstaller -F outage_config.py

which creates 'outage_config.exe' (Windows) in the subdirectory 'dist'.
This is usually renamed to outage_config_win.exe and put on the '/boot'
partition of the Mini-Monitor SD card.  If pyinstaller is run on a Mac,
'outage_config' is created, which is typically renamed to 'outage_config_mac'
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
        internet_type = inet_type.get()
        w_ssid = wifi_ssid_entry.get()
        w_pass = wifi_pass_entry.get()
        modem_type = modem_values[cell_modem_combo.current()]
        # other_settings_fn is global and already set

        # Do a few input checks
        if len(logger_id.strip())==0:
            tkinter.messagebox.showerror('No Site Name', 'You must enter a Site Name.')
            return -1

        if internet_type=='wifi':
            if len(w_ssid.strip())==0:
                tkinter.messagebox.showerror('No WiFi Name', 'You must enter a WiFi Network Name.')
                return -1

        substitutions = [
            (r'LOGGER_ID\s*=', "LOGGER_ID = '%s'" % logger_id),
            (r'USE_CELL_MODEM\s*=', 'USE_CELL_MODEM = %s' % ('True' if internet_type=='cellular' else 'False')),
            (r'CELL_MODEM_MODEL\s*=', "CELL_MODEM_MODEL = '%s'" % modem_type),
            (r'outage_monitor.OutageMonitor', "'outage_monitor.OutageMonitor',   # Detects Power Outages through state of GPIO pin"),
            (r'sys_info.SysInfo', "'sys_info.SysInfo',               # System uptime, CPU temperature, software version"),
        ]

        # loop through the file containing other settings and
        # add to the substitution list
        if other_settings_fn:
            for line in open(other_settings_fn):
                line = line.strip()   # get rid of the line ending characters
                if re.search(r'^\s*#', line) is None:   # ignore comment lines
                    flds = line.split('\t')
                    if len(flds) == 2:
                        substitutions.append(flds)

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
        sup_fn = os.path.join(THIS_DIR, 'pi_logger/wpa_supplicant.conf')
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
    cell_frame.grid_remove()
    i_type = inet_type.get()
    if i_type=='ethernet':
        pass
    elif i_type=='wifi':
        wifi_frame.grid()
    elif i_type=='cellular':
        cell_frame.grid()

def select_other_setting():
    global other_settings_fn
    other_settings_fn = tkinter.filedialog.askopenfilename()
    other_settings_var.set(SETTINGS_FILE_TMPL % other_settings_fn)

root = Tk()
root.title('Mini-Monitor Configuration')

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
tkinter.ttk.Label(mainframe, text='Enter Short Name for this Site (20 character max, no spaces):').grid(
    column=0, row=0, sticky=W)
site_entry = tkinter.ttk.Entry(mainframe, width=20)
site_entry.grid(column=0, row=1, sticky=W)

#---- Internet Access
inet_frame = tkinter.ttk.LabelFrame(mainframe, text='Internet Access Type')
inet_frame.grid(column=0, row=6, sticky=W)
inet_type = StringVar()
tkinter.ttk.Radiobutton(inet_frame, text='WiFi', variable=inet_type, value='wifi', command=inet_visibility).grid(column=0, row=0)
tkinter.ttk.Radiobutton(inet_frame, text='Ethernet', variable=inet_type, value='ethernet', command=inet_visibility).grid(column=1, row=0)
tkinter.ttk.Radiobutton(inet_frame, text='Cellular (requires modem)', variable=inet_type, value='cellular', command=inet_visibility).grid(column=2, row=0)
inet_type.set('ethernet')
for child in inet_frame.winfo_children():
    child.grid_configure(padx=10, pady=5)

# WiFi credentials
wifi_frame = tkinter.ttk.Frame(mainframe)
wifi_frame.grid(column=0, row=7, sticky=W)
tkinter.ttk.Label(wifi_frame, text='WiFi Network Name:').grid(column=0, row=0, sticky=E)
wifi_ssid_entry = tkinter.ttk.Entry(wifi_frame, width=30)
wifi_ssid_entry.grid(column=1, row=0)
tkinter.ttk.Label(wifi_frame, text='WiFi Password (leave blank if Open network):').grid(column=0, row=1, sticky=E)
wifi_pass_entry = tkinter.ttk.Entry(wifi_frame, width=30)
wifi_pass_entry.grid(column=1, row=1, sticky=W)
for child in wifi_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Cellular Modem Type
cell_frame = tkinter.ttk.Frame(mainframe)
cell_frame.grid(column=0, row=8, sticky=W, padx=5, pady=5)
tkinter.ttk.Label(cell_frame, text='Cellular Modem Model:').grid(column=0, row=0, sticky=E)
cell_modem = StringVar()
cell_modem_combo = tkinter.ttk.Combobox(cell_frame, textvariable=cell_modem)
cell_modem_combo.grid(column=1, row=0, padx=5, pady=5)
modem_text = ('Huawei E173', 'Huawei E3276', 'Huawei E1756C', 'ZTE MF197 Serial')
modem_values = ('E173', 'E3276', 'E1756C', 'MF197')
cell_modem_combo['values'] = modem_text
cell_modem_combo.state(['readonly'])
cell_modem_combo.current(0)

# Select Other Settings File
SETTINGS_FILE_TMPL = 'Other Settings File: %s'
other_settings_fn = ''
other_settings_var = StringVar()
other_settings_var.set(SETTINGS_FILE_TMPL % other_settings_fn)
other_frame = tkinter.ttk.Frame(mainframe)
other_frame.grid(column=0, row=9, sticky=W)
tkinter.ttk.Label(other_frame, text='Select File containing Other Settings:').grid(column=0, row=0, sticky=W, padx=5, pady=5)
tkinter.ttk.Button(other_frame, text='Select File', command=select_other_setting).grid(column=1, row=0, sticky=W, padx=5, pady=5)
tkinter.ttk.Label(mainframe, textvariable=other_settings_var).grid(column=0, row=10, sticky=W)

tkinter.ttk.Separator(mainframe, orient=HORIZONTAL).grid(column=0, row=11, sticky='EW')
tkinter.ttk.Button(mainframe, text='Store these Configuration Settings', command=store_settings).grid(column = 0, row=12)

# Add some padding to all widgets in mainframe
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# run routines to get initial visibility correct
inet_visibility()

root.mainloop()
