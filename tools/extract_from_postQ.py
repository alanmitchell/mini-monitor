#!/usr/bin/env python3
"""Script to extract the readings from a Raspberry Pi mini-monitor Post
queue (/var/local/postQ.sqlite).  These are readings gathered on the Pi
that were not successfully posted. This script was specifically designed for
the ACEP Outage meter, and only extracts the 'OutageMeter1_state' readings.
The extracted readings are written to a CSV file containing a UNIX timestamp
and the state of the AC power (1 = On, 0 = Off).

Usage:

    python3 extract_from_postQ.py <name of Post queue, usually 'postQ.sqlite'> <CSV output file name>

    e.g.
    python3 extract_from_postQ.py postQ.sqlite readings.csv

"""

import sys
import sqlite3
from pickle import loads

post_file_name = sys.argv[1]
out_file_name = sys.argv[2]

# connect to the SQLite database file
with sqlite3.Connection(post_file_name) as conn:

    with open(out_file_name, 'w') as fout:
        
        fout.write('ts,pwr_state\n')  # header row for CSV file
        for id, item in conn.execute('select id, item from queue'):
            # item is a Python pickled string, so unpickle it.
            # The result is a dictionary containing the Post information, 
            # including a set of readings that are being posted.
            rec = loads(item)
            for read in rec['readings']:
                # just save the power status readings
                if read[1] == 'OutageMeter1_state':
                    fout.write(f'{read[0]},{read[2]}\n')
