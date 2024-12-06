#!/usr/bin/env python

"""Input module for ERA data."""

import os, sys

import numpy as np
import xarray as xr


def era_name_analyzer(era_name):
    """
    Analyze the ERA name and return the properties.

    Parameters
    ----------
    era_name : str
        The name of the ERA file.

    Returns
    -------
    era_name_props : dict
        The properties of the ERA file.

    Notes
    -----
    The ERA name assumed to be in the form of 
    {modelname}-{data_type}-{region}-{year}-{month}-{day}.nc.

    """
    fullpath = os.path.dirname(era_name)
    basename = os.path.basename(era_name)

    base, ext = os.path.splitext(basename)
    modelname, data_type, region, year, month, day = base.split("-")

    era_name_props = {}
    era_name_props["fullpath"] = fullpath
    era_name_props["modelname"] = modelname
    era_name_props["data_type"] = data_type
    era_name_props["region"] = region
    era_name_props["year"] = year
    era_name_props["month"] = month
    era_name_props["day"] = day

    return era_name_props


def era_name_converter(era_name, mode="3d_to_2d"):
    """
    Convert the ERA name.

    Parameters
    ----------
    era_name : str
        The name of the ERA file.

    mode : str, optional
        The mode of the conversion. Default is "3d_to_2d".
        - "3d_to_2d" : convert 3d to 2d.
    
    Returns
    -------
    era_name_converted : str
        The converted ERA name.
    """
    if mode == "3d_to_2d":

        era_name_props = era_name_analyzer(era_name)

        era_name_converted = (
            "{fullpath}/{modelname}-2d-{region}-{year}-{month}.nc".format(
                **era_name_props
            )
        )

    return era_name_converted


def open_era(era3d_name, add_pressure=True, qmin=1.1e-9, **kwargs):
    """
    Open the ERA data.

    Parameters
    ----------
    era3d_name : str
        The name of the ERA 3D file.

    add_pressure : bool, optional
        Whether to add pressure. Default is True.
    
    qmin : float, optional
        The minimum value of q. 
        Values below this threshold will be clipped.
        Default is 1.1e-9.

        
    Returns
    -------
    era : xarray.Dataset
        The opened ERA dataset.
    
    """
    # open datasets
    era3d = xr.open_dataset(era3d_name)

    era2d_name = era_name_converter(era3d_name, mode="3d_to_2d")
    era2d = xr.open_dataset(era2d_name, chunks={"time": 1})

    # only select 3d timeslot
    era2d = era2d.sel(time=era3d.time)

    era = xr.merge([era2d, era3d])

    if add_pressure:
        era["p"] = calc_pressure(era)

    era["q"] = era["q"].clip(min=qmin)

    return era


def calc_pressure(era):
    """
    Calculate pressure from ERA data.

    Parameters
    ----------
    era : xarray.Dataset
        The ERA dataset.
    
    Returns
    -------
    p : xarray.DataArray
        The calculated pressure.

    Notes
    -----
    The pressure is calculated as follows:
    p = B * ps + A,
    where p is the pressure, ps is the surface pressure,
    """
    # calculate pressure
    A = era["hyam"]
    B = era["hybm"]
    ps = era["SP"]

    p = B * ps + A
    
    p = p.rename({'nhym': 'lev'})
    p.attrs = dict(long_name="atmospheric pressure", units="Pa")


    return p
