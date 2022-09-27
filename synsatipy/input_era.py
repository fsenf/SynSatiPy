#!/usr/bin/env python

import os, sys

import numpy as np
import xarray as xr

def era_name_analyzer(era_name):
        
    fullpath = os.path.dirname( era_name )
    basename = os.path.basename( era_name )
    
    base, ext = os.path.splitext( basename )
    modelname, data_type, region, year, month, day = base.split('-') 
    
    
    era_name_props = {}
    era_name_props['fullpath']  = fullpath
    era_name_props['modelname'] = modelname
    era_name_props['data_type'] = data_type
    era_name_props['region']    = region
    era_name_props['year']      = np.int( year )
    era_name_props['month']     = np.int( month )
    era_name_props['day']       = np.int( day )
    
    
    return era_name_props


def era_name_converter( era_name, mode = '3d_to_2d' ):
    
    if mode == '3d_to_2d':
        
        era_name_props = era_name_analyzer(era_name)
        
        era_name_converted = '{fullpath}/{modelname}-2d-{region}-{year}-{month}.nc'.format(**era_name_props)

    return era_name_converted


def open_era( era3d_name, add_pressure = True):
    
    
    # open datasets
    era3d = xr.open_dataset( era3d_name)

    era2d_name = era_name_converter( era3d_name, mode = '3d_to_2d')
    era2d = xr.open_dataset( era2d_name, chunks = {'time':1}  )
    
    # only select 3d timeslot
    era2d = era2d.sel( time = era3d.time )
    
    era = xr.merge ([era2d, era3d])
    
    if add_pressure:
        era['p'] = calc_pressure( era )  
       
    return era


def calc_pressure( era ):
    
    # calculate pressure
    A = era['hyam']
    B = era['hybm']
    ps = era['SP']

    p = B * ps + A
    p.attrs = dict( long_name = 'atmospheric pressure', units = 'Pa')
    
    return p
    

