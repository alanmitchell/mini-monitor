'''Contains utilities useful to configuring the mini-monitor
settings file.
'''

def wpa_sup_file(ssid=None, psk=None):
    """Returns the contents of a wpa_supplicant.conf file
    setup to connect to the WiFi network with an SSID of
    'ssid' and password of 'psk'.  If the 'ssid' is None
    then the file contents will not include WiFi connection
    info and will be suitable for Ethernet or other means
    of connecting to the Internet.
    """
    # start of the file
    header = '''country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
'''

    # WiFi connection part of file
    wifi_info = '''network={
    ssid="%s"
    scan_ssid=1
    psk="%s"
}
'''

    if ssid is None:
        return header

    return header + (wifi_info % (ssid, psk))

def replace_setting(file_contents, setting, new_value):
    """Replaces a setting in a Python settings file
    with a new value.
    PARAMETERS
    ----------
    'file_contents': The string contents of the settings file to alter.
    'setting': The name of the setting in the file to alter.
    'new_value': The new value for the setting, expressed as a string.
    RETURNS
    -------
    The altered contents of the settings file.  Uses Linux line endings.
    If the setting is not found in the contents, the contents are not
    altered.
    """

    lines = file_contents.splitlines()
    test_str = setting + '='
    new_lines = []
    for line in lines:
        if line.replace(' ', '').startswith(test_str):
            new_lines.append('%s = %s' % (setting, new_value))
        else:
            new_lines.append(line)

    return chr(10).join(new_lines)
