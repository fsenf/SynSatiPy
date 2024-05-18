# standard packages
import numpy as np
import xarray as xr

# nextgems related packages
from easygems.healpix import attach_coords
import healpy
import intake

from synsatipy.utils.spacetools import lonlat2azizen


def open_ngdataset(cat_path, **kwargs):

    zoom = kwargs.get("zoom", 9)

    cat = intake.open_catalog(cat_path)

    dset = (
        cat.ICON.ngc4008a(zoom=zoom, time="PT15M")  # chunks="auto",
        .to_dask()
        .pipe(attach_coords)
    )

    return dset


def get_index_for_zenith_mask(dset, max_zenith=80):

    azi, zen = lonlat2azizen(dset["lon"], dset["lat"])

    zen_mask = zen <= max_zenith

    regional_index = np.where(zen_mask)[0]

    return regional_index


def get_index_for_regional_extend(dset, extend):

    lon_extend = extend[0:2]
    lat_extend = extend[2:4]

    lon_mask = (dset["lon"] > lon_extend[0]) & (dset["lon"] < lon_extend[1])
    lat_mask = (dset["lat"] > lat_extend[0]) & (dset["lat"] < lat_extend[1])

    mask = lon_mask & lat_mask

    regional_index = np.where(mask)[0]

    return regional_index


def input_regional_nextgems(
    cat_path, mask_type=None, extend=None, time=None, max_zenith=80, **kwargs
):

    dset = open_ngdataset(cat_path, **kwargs)

    if mask_type == "regional" and extend is not None:
        regional_index = get_index_for_regional_extend(dset, extend)
        dset_reg = dset.isel(cell=regional_index)

    elif mask_type == "zenith":
        regional_index = get_index_for_zenith_mask(dset, max_zenith=max_zenith)
        dset_reg = dset.isel(cell=regional_index)

    else:
        dset_reg = dset  # be careful here

    if time is not None:
        dset_reg_sub = dset_reg.sel(
            time=[
                time,
            ]
        )

    else:
        dset_reg_sub = dset

    return dset_reg_sub


def nextgems_variable_mapping(
    dset,
):

    d_renamed = xr.Dataset()

    # variables

    icon2era = {
        "pfull": "p",
        "ta": "t",
        "hus": "q",
        "clw": "clwc",
        "cli": "ciwc",
        "qs": "cswc",
        "ts": "SKT",
        "t_2m": "T2M",
        "pres_sfc": "SP",
        "clc": "cc",
    }

    for iname in icon2era:
        ename = icon2era[iname]

        d_renamed[ename] = dset[iname]

    # coordinates
    d_renamed = d_renamed.rename_dims({"level_full": "lev"})

    return d_renamed


def open_nextgems(cat_path, name_remapping=True, **kwargs):

    dset = input_regional_nextgems(cat_path, **kwargs)

    dset["t_2m"] = dset["ta"].isel(level_full=-1)
    dset["pres_sfc"] = dset["pfull"].isel(level_full=-1)

    q_tot = dset["clw"] + dset["cli"] + dset["qs"]
    q_tot_thresh = 1e-9

    O = xr.zeros_like(dset["clw"])
    I = xr.ones_like(dset["clw"])

    dset["clc"] = xr.where(q_tot < q_tot_thresh, O, I)

    dset = dset.transpose("time", "cell", "level_full", "level_half")

    if name_remapping:
        return nextgems_variable_mapping(dset)
    else:
        return dset
