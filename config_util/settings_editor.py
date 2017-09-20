'''This is a small GUI utility that helps to configure the Mini-Monitor
by modifying values in the settings.py file and by setting up WiFi
Internet access if requested.
'''

from Tkinter import *
import ttk
import tkMessageBox
import tkFileDialog
import tkFont
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
        use_gas = True if enable_gas.get()=='1' else False
        meter_ids = meter_ids_entry.get()
        internet_type = inet_type.get()
        w_ssid = wifi_ssid_entry.get()
        w_pass = wifi_pass_entry.get()
        modem_type = modem_values[cell_modem_combo.current()]
        # other_settings_fn is global and already set

        # Do a few input checks
        if len(logger_id.strip())==0:
            tkMessageBox.showerror('No Site Name', 'You must enter a Site Name.')
            return -1

        if internet_type=='wifi':
            if len(w_ssid.strip())==0:
                tkMessageBox.showerror('No WiFi Name', 'You must enter a WiFi Network Name.')
                return -1

        substitutions = [
            (r'LOGGER_ID\s*=', "LOGGER_ID = '%s'" % logger_id)
        ]

        if use_gas:
            substitutions += [
                (r'ENABLE_METER_READER\s*=', 'ENABLE_METER_READER = True'),
                (r'METER_IDS\s*=', 'METER_IDS = [%s]' % meter_ids),
                (r'METER_MULT\s*=', 'METER_MULT = 1000.0'),
            ]
        else:
            substitutions += [
                (r'ENABLE_METER_READER\s*=', 'ENABLE_METER_READER = False'),
            ]

        substitutions += [
            (r'USE_CELL_MODEM\s*=', 'USE_CELL_MODEM = %s' % ('True' if internet_type=='cellular' else 'False')),
            (r'CELL_MODEM_MODEL\s*=', "CELL_MODEM_MODEL = '%s'" % modem_type),
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
            f.write(unicode(file_contents))

        # Make the proper wpa_supplicant.conf file.
        if internet_type=='wifi':
            file_contents = setup_utils.wpa_sup_file(ssid=w_ssid, psk=w_pass)
        else:
            file_contents = setup_utils.wpa_sup_file()
        sup_fn = os.path.join(THIS_DIR, 'pi_logger/wpa_supplicant.conf')
        with io.open(sup_fn, 'w', newline='\n') as f:
            f.write(unicode(file_contents))

        msg = 'The Settings were Successfully Stored!  You can now close the application or modify settings and Store again.'
        tkMessageBox.showinfo('Success', msg)
        return 0

    except Exception as e:
        tkMessageBox.showerror('Error Occurred', 'An Error occurred while attempting to store settings:\n%s' % str(e))
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

def gas_id_visibility():
    """Manage visibility of Gas Meter ID widgets.
    """
    if enable_gas.get()=='1':
        meter_ids_label.grid()
        meter_ids_entry.grid()
    else:
        meter_ids_label.grid_remove()
        meter_ids_entry.grid_remove()


def select_other_setting():
    global other_settings_fn
    other_settings_fn = tkFileDialog.askopenfilename()
    other_settings_var.set(SETTINGS_FILE_TMPL % other_settings_fn)

root = Tk()
root.title('Mini-Monitor Configuration')

# Increase font sizes a bit
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=11)
text_font = tkFont.nametofont("TkTextFont")
text_font.configure(size=11)

# Main Frame to hold all widgets
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky='EWNS')
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Site ID entry
ttk.Label(mainframe, text='Enter Short Name for this Site (20 character max, no spaces):').grid(
    column=0, row=0, sticky=W)
site_entry = ttk.Entry(mainframe, width=20)
site_entry.grid(column=0, row=1, sticky=W)

# Gas Meter Reader related
enable_gas = StringVar()
enable_gas_check = ttk.Checkbutton(mainframe,
                                   text='Enable Meter Reader',
                                   variable=enable_gas,
                                   command=gas_id_visibility)
enable_gas.set('1')
enable_gas_check.grid(column=0, row=3, sticky=W)
meter_ids_label = ttk.Label(mainframe, text='Enter Meter ID. Separate Multiple IDs with commas. Leave Blank to read All meters.')
meter_ids_label.grid(column=0, row=4, sticky=W)
meter_ids_entry = ttk.Entry(mainframe, width=50)
meter_ids_entry.grid(column=0, row=5, sticky=W)

#---- Internet Access
inet_frame = ttk.LabelFrame(mainframe, text='Internet Access Type')
inet_frame.grid(column=0, row=6, sticky=W)
inet_type = StringVar()
ttk.Radiobutton(inet_frame, text='WiFi', variable=inet_type, value='wifi', command=inet_visibility).grid(column=0, row=0)
ttk.Radiobutton(inet_frame, text='Ethernet', variable=inet_type, value='ethernet', command=inet_visibility).grid(column=1, row=0)
ttk.Radiobutton(inet_frame, text='Cellular (requires modem)', variable=inet_type, value='cellular', command=inet_visibility).grid(column=2, row=0)
inet_type.set('wifi')
for child in inet_frame.winfo_children():
    child.grid_configure(padx=10, pady=5)

# WiFi credentials
wifi_frame = ttk.Frame(mainframe)
wifi_frame.grid(column=0, row=7, sticky=W)
ttk.Label(wifi_frame, text='WiFi Network Name:').grid(column=0, row=0, sticky=E)
wifi_ssid_entry = ttk.Entry(wifi_frame, width=30)
wifi_ssid_entry.grid(column=1, row=0)
ttk.Label(wifi_frame, text='WiFi Password (leave blank if Open network):').grid(column=0, row=1, sticky=E)
wifi_pass_entry = ttk.Entry(wifi_frame, width=30)
wifi_pass_entry.grid(column=1, row=1, sticky=W)
for child in wifi_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Cellular Modem Type
cell_frame = ttk.Frame(mainframe)
cell_frame.grid(column=0, row=8, sticky=W, padx=5, pady=5)
ttk.Label(cell_frame, text='Cellular Modem Model:').grid(column=0, row=0, sticky=E)
cell_modem = StringVar()
cell_modem_combo = ttk.Combobox(cell_frame, textvariable=cell_modem)
cell_modem_combo.grid(column=1, row=0, padx=5, pady=5)
modem_text = ('Huawei E173', 'Huawei E3276', 'Huawei E1756C')
modem_values = ('E173', 'E3276', 'E1756C')
cell_modem_combo['values'] = modem_text
cell_modem_combo.state(['readonly'])
cell_modem_combo.current(0)

# Select Other Settings File
SETTINGS_FILE_TMPL = 'Other Settings File: %s'
other_settings_fn = ''
other_settings_var = StringVar()
other_settings_var.set(SETTINGS_FILE_TMPL % other_settings_fn)
other_frame = ttk.Frame(mainframe)
other_frame.grid(column=0, row=9, sticky=W)
ttk.Label(other_frame, text='Select File containing Other Settings:').grid(column=0, row=0, sticky=W, padx=5, pady=5)
ttk.Button(other_frame, text='Select File', command=select_other_setting).grid(column=1, row=0, sticky=W, padx=5, pady=5)
ttk.Label(mainframe, textvariable=other_settings_var).grid(column=0, row=10, sticky=W)

ttk.Separator(mainframe, orient=HORIZONTAL).grid(column=0, row=11, sticky='EW')
ttk.Button(mainframe, text='Store these Configuration Settings', command=store_settings).grid(column = 0, row=12)

# Add some padding to all widgets in mainframe
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# run routines to get initial visibility correct
inet_visibility()

root.mainloop()
