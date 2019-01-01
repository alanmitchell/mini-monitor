"""Functions related to detecting and posting changes in 
a set of sensor readings.
"""

def find_changes(vals, threshold=None, change_pct=0.02, max_interval=None):
    """Returns an array of index values that point at the values in the 'vals'
    array that represent signficant changes.  'threshold' is the absolute amount
    that a value must change before being included.  If 'threshold' is None, 
    'change_pct' is used to determine a threshold change by multiplying
    'change_pct' by the difference between the minimum and maximum value.  If
    'max_interval' is provided, it will be the maximum allowed separation between
    returned index values. This forces some some points to be returned even if
    no signficant change has occurred.
    Index 0, pointing at the first value is always returned.
    """
    
    # special case of no values passed
    if len(vals) == 0:
        return []
    
    if threshold is None:
        # compute the threshold difference that constitutes a change
        # from the change_pct parameter
        threshold = (max(vals) - min(vals)) * change_pct
        if threshold == 0.0:
            threshold = 0.01   # keep it from showing every point

    # Start with the first value
    final_ixs = [0]
    last_val = vals[0]
    last_ix = 0
    
    for ix in range(1, len(vals)):
        v = vals[ix]
        include_this_index = False
        if abs(v - last_val) >= threshold:
            # if the prior value was not included, include it
            if last_ix != ix - 1:
                final_ixs.append(ix - 1)
            include_this_index = True
        elif max_interval is not None and ix - last_ix >= max_interval:
            include_this_index = True
        
        if include_this_index:
            final_ixs.append(ix)
            last_val = v
            last_ix = ix
    
    return final_ixs

def make_post_lines(sensor_id, time_stamps, values, change_threshold, max_interval):
    """Returns an array of lines to post to the MQTT broker.  Only posts changes in 
    values.
    'sensor_id': sensor ID to use for each line
    'time_stamps': numpy array of time stamps associated with the values
    'values': numpy array of values to scan for changes and post accordingly
    'change_threshold': amount of change that needs to occur before inclusion
    'max_interval': maximum number of points to separate posts.  Will post w/o a change to meet this.
    """
    # find the indexes to include in the post lines
    ixs = find_changes(values, change_threshold, max_interval=max_interval)
    ts_incl = time_stamps[ixs]
    val_incl = values[ixs]
    return ['%s\t%s\t%s' % (ts, sensor_id, val) for ts, val in zip(ts_incl, val_incl)]
