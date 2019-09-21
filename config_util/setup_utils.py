'''Contains utilities useful to configuring the mini-monitor
settings file.
'''

import re

def wpa_sup_file(ssid=None, psk=None):
    """Returns the contents of a wpa_supplicant.conf file
    setup to connect to the WiFi network with an SSID of
    'ssid' and password of 'psk'.  If the 'ssid' is None
    then the file contents will not include WiFi connection
    info and will be suitable for Ethernet or other means
    of connecting to the Internet.
    """
    # start of the file
    header = '''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
'''

    # WiFi connection part of file
    wifi_info = '''network={
    ssid="%s"
    scan_ssid=1
    psk="%s"
}
'''
    # Open WiFi connection version
    wifi_open_info = '''network={
    ssid="%s"
    scan_ssid=1
    key_mgmt=NONE
}
'''

    if ssid is None:
        # Not a WiFi connection
        return header
    elif psk.strip():
        # Secure WiFi
        return header + (wifi_info % (ssid, psk))
    else:
        # Open WiFi
        return header + (wifi_open_info % ssid)

def replace_line(file_contents, replacements):
    """Replaces lines in a file with a new line, based on search
    expressions.

    PARAMETERS
    ----------
    'file_contents': The string contents of the file to alter.
    'replacements': A list of two-tuples describing the replacements.
        The first item in the tuple is a RegEx search expression identifying
        a line to be replaced; the second tuple item is the the new line to
        substitute.
    RETURNS
    -------
    The altered contents of the file.  Uses Linux line endings.
    If the setting is not found in the contents, the contents are not
    altered.
    """

    lines = file_contents.splitlines()
    new_lines = []
    for line in lines:
        sub_made = False
        for match_expr, new_line in replacements:
            if re.search(match_expr, line):
                new_lines.append(new_line)
                sub_made = True
                break
        if not sub_made:
            new_lines.append(line)

    return chr(10).join(new_lines)
