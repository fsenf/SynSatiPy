#!/usr/bin/env python


######################################################################
######################################################################

'''
Set of tools for IO of either obs or sim.
'''

######################################################################
######################################################################

import numpy as np
import datetime

######################################################################
######################################################################

def convert_time(t, roundTo = 60.):

    '''
    Utility converts between two time formats A->B or B->A: 
    

    Parameters
    ----------
    t : float or datetime object
        time 
        A = either float as %Y%m%d.%f where %f is fraction of the day
        B = datetime object


    Returns
    -------
    tout : datetime object or float
        time, counterpart to t
    '''

    t0 = datetime.datetime(1970, 1, 1)

    if type(t) == type(t0):

        tout = np.int( t.strftime('%Y%m%d') )
        date = datetime.datetime.strptime(str(tout), '%Y%m%d')

        dt = (t - date).total_seconds()
        frac =  dt / (24 * 3600)

        tout +=  frac
    else:
        
        date = np.int32(t)
        frac = t - date

        tout = datetime.datetime.strptime(str(date), '%Y%m%d')
        tout += datetime.timedelta( days = frac )
        tout = roundTime( tout, roundTo = roundTo )

    return tout 
        


######################################################################
######################################################################

def convert_timevec( timevec ):
    '''
    Utility converts between an array of two time formats A->B or B->A: 
    

    Parameters
    ----------
    timevec : list or array
        time list
        A = either float as %Y%m%d.%f where %f is fraction of the day
        B = datetime object


    Returns
    -------
    tout : list
        list of datetime objects or floats
        time, counterpart to t
    '''
    
    times = []
    for tfloat in timevec:
        times += [ convert_time( tfloat ), ]
    
    times = np.array( times )
    
    return times

######################################################################
######################################################################


def roundTime(dt = None, roundTo = 60):

    """


    Round a datetime object to any time laps in seconds.


    Parameters
    ----------
    dt : datetime object, optional, default now
        time to be round
    
    roundTo : float, optional, default 1 minute
         Closest number of seconds to round to, default 1 minute.


    Returns
    --------
    t : datetime object
        rounded time

    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None : dt = datetime.datetime.now()

    seconds = (dt - dt.min).seconds

    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo

    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

######################################################################
######################################################################

def round2day(t):
    
    '''
    Rounds a np.datetime64 object to one day.
    
    
    Parameters
    ----------
    t : numpy datetime64 object
        input time
        
    
    Returns
    --------
    tout : numpy datetime64 object
        rounded output time
     
    '''
    
    dt = np.timedelta64(12, 'h')
    
    return (t + dt).astype(dtype = 'datetime64[D]')

######################################################################
######################################################################
