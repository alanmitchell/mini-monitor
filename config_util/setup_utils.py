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

def replace_line(file_contents, match_expr, new_line):
    """Replaces a line in a file with a new line. Finds the target
    line with a RegEx expression.

    PARAMETERS
    ----------
    'file_contents': The string contents of the file to alter.
    'match_expr': A RegEx expression that will match the line to replace
    'new_line': The new line, w/o any line endings.
    RETURNS
    -------
    The altered contents of the file.  Uses Linux line endings.
    If the setting is not found in the contents, the contents are not
    altered.
    """

    lines = file_contents.splitlines()
    new_lines = []
    for line in lines:
        if re.search(match_expr, line):
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    return chr(10).join(new_lines)
