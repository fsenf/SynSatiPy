#!/usr/bin/env python

import os, sys

import numpy as np
import xarray as xr


import synsatipy.utils.timetools as timetools


def icon_name_analyzer(icon_name):

    """
    Analyze the ICON name and return the properties.

    Parameters
    ----------
    icon_name : str
        The name of the ICON file.

    Returns
    -------
    icon_name_props : dict
        The properties of the ICON file.

    Notes
    -----
    The ICON name assumed to be in the form of
    {data_type}_{variable_stack}_{domain}_{level_type}_{time_str}_{postproc_suffix}.nc.
    """

    fullpath = os.path.dirname(icon_name)
    basename = os.path.basename(icon_name)

    base, ext = os.path.splitext(basename)

    # first decomposition type
    icon_name_props = {}
    icon_name_props["fullpath"] = fullpath

    if "ifces2" in fullpath:
        icon_name_props["flavor"] = "ifces2"

        base = base.replace("full_", "full-")

        # 2d_cloud_DOM01_ML_20200912T000000Z_regrid7km.nc
        data_type, variable_stack, domain, level_type, time_str, postproc_suffix = (
            base.split("_")
        )

        icon_name_props["data_type"] = data_type
        icon_name_props["variable_stack"] = variable_stack.replace("full-", "full_")
        icon_name_props["domain"] = domain

        icon_name_props["level_type"] = level_type
        icon_name_props["time_str"] = time_str
        icon_name_props["postproc_suffix"] = postproc_suffix

    return icon_name_props


def icon_name_creator(icon_name_props):

    """
    Create the ICON name.

    Parameters
    ----------
    icon_name_props : dict
        The properties of the ICON file.
        -  "flavor" : str
           "flavor" of the ICON file. Default is "ifces2".
   

    Returns
    -------
    icon_name : str
        The ICON name.

    Notes
    -----
    The ICON name assumed to be in the form of
    {data_type}_{variable_stack}_{domain}_{level_type}_{time_str}_{postproc_suffix}.nc.
    """

    flavor = icon_name_props["flavor"]

    if flavor == "ifces2":

        icon_name = "{fullpath}/{data_type}_{variable_stack}_{domain}_{level_type}_{time_str}_{postproc_suffix}.nc".format(
            **icon_name_props
        )

    return icon_name


def icon_variable_mapping(
    dset,
):
    
    """
    Rename ICON variables to ERA5 variables.

    Parameters
    ----------
    dset : xarray.Dataset
        The ICON dataset.

    Returns
    -------
    d_renamed : xarray.Dataset
        The renamed ICON dataset.

    """

    d_renamed = xr.Dataset()

    # variables

    icon2era = {
        "pres": "p",
        "temp": "t",
        "qv": "q",
        "qc": "clwc",
        "qi": "ciwc",
        "qs": "cswc",
        "t_s": "SKT",
        "t_2m": "T2M",
        "pres_sfc": "SP",
        "clc": "cc",
    }

    for iname in icon2era:
        ename = icon2era[iname]

        d_renamed[ename] = dset[iname]

    # coordinates
    d_renamed = d_renamed.rename_dims({"height": "lev"})

    return d_renamed


def open_icon(icon3d_name, qmin=1.1e-9, name_remapping=True):

    """
    Open ICON dataset.

    Parameters
    ----------
    icon3d_name : str
        The name of the ICON 3D file.

    qmin : float, optional
        Minimum value of qv. Default is 1.1e-9.
        Values below this threshold are clipped.
    
    name_remapping : bool, optional
        Whether to remap the variable names. Default is True.
    
    Returns
    -------
    icon : xarray.Dataset
        The ICON dataset.

    """

    input_options = {"chunks": "auto"}

    # open base datasets
    icon3dbase = xr.open_dataset(icon3d_name, **input_options)

    icon_name_props = icon_name_analyzer(icon3d_name)

    # open hydrometeors
    icon_name_props.update({"variable_stack": "full_qmix"})
    icon_others_name = icon_name_creator(icon_name_props)
    icon3dqmix = xr.open_dataset(icon_others_name, **input_options)

    icon3d = xr.merge([icon3dbase, icon3dqmix])

    # open surfacer props
    icon_name_props.update(
        {
            "data_type": "2d",
            "variable_stack": "surface",
        }
    )
    icon_others_name = icon_name_creator(icon_name_props)
    icon2d = xr.open_dataset(icon_others_name, **input_options)

    # only select 3d timeslot
    icon2d = icon2d.sel(time=icon3d.time).squeeze(dim="height")

    # merge dataset
    icon = xr.merge([icon2d, icon3d])

    # modify variables
    icon["qv"] = icon["qv"].clip(min=qmin)
    icon["clc"] = icon["clc"] / 100.0  # unit change from [0, 100] % to [0, 1]

    # set correct time object
    t = timetools.convert_timevec(icon.time.data)
    icon = icon.assign_coords({"time": t})

    if name_remapping:
        return icon_variable_mapping(icon)
    else:
        return icon
