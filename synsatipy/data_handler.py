#!/usr/bin/env python


import numpy as np
import datetime
import xarray as xr


from synsatipy.starter import pyrttov

import synsatipy.input_icon as input_icon
import synsatipy.input_era as input_era
import synsatipy.input_nextgems as input_nextgems

from synsatipy.utils.spacetools import lonlat2azizen


######################################################################
######################################################################


def dt2cal(dt):
    """
    Convert array of datetime64 to a calendar array of year, month, day, hour,
    minute, seconds, microsecond with these quantites indexed on the last axis.

    Parameters
    ----------
    dt : datetime64 array (...)
        numpy.ndarray of datetimes of arbitrary shape

    Returns
    -------
    cal : uint32 array (..., 7)
        calendar array with last axis representing year, month, day, hour,
        minute, second, microsecond
    """

    # allocate output
    out = np.empty(dt.shape + (7,), dtype="u4")
    # decompose calendar floors
    Y, M, D, h, m, s = [dt.astype(f"M8[{x}]") for x in "YMDhms"]
    out[..., 0] = Y + 1970  # Gregorian Year
    out[..., 1] = (M - Y) + 1  # month
    out[..., 2] = (D - M) + 1  # dat
    out[..., 3] = (dt - D).astype("m8[h]")  # hour
    out[..., 4] = (dt - h).astype("m8[m]")  # minute
    out[..., 5] = (dt - m).astype("m8[s]")  # second
    out[..., 6] = (dt - s).astype("m8[us]")  # microsecond
    return out



######################################################################
######################################################################


def autodetect_model_by_filename(fname):
    """
    Autodetects the model based on the filename.

    Parameters
    ----------
    fname : str
        The filename to check for model keywords.

    Returns
    -------
    model : str
        The detected model name.

    Raises
    ------
    ValueError
        If the model cannot be autodetected.
    """


    model = None

    era_keys = ["era"]

    for k in era_keys:
        if k in fname:
            model = "era"

    icon_keys = ["icon", "ifces"]

    for k in icon_keys:
        if k in fname:
            model = "icon"

    if model is None:
        raise ValueError("Model autodetect failed!")

    return model


######################################################################
######################################################################


class DataHandler(object):
    """
    Handles data operations for different models.

    Parameters
    ----------
    model : str, optional
        The model to use. Default is "auto".
        model can be "era", "icon", "nextgems" or "auto".
        "auto" will try to autodetect the model based on the filename.
    
    return_profile : bool, optional
        Whether to return profile data. Default is True.

    **kwargs : dict
        Additional keyword arguments.
    """

    def __init__(self, model="auto", return_profile=True, **kwargs):

        self.model = model

        return

    def open_data(self, filename, **kwargs):
        """
        Opens data from a file.

        Parameters
        ----------
        filename : str
            The name of the file to open.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        data : object
            The opened data.
        """
        isel = kwargs.pop("isel", None)
        profile_dimensions = kwargs.pop("profile_dimensions", ["time", "lon", "lat"])

        if self.model == "auto":
            model = autodetect_model_by_filename(filename)
        else:
            model = self.model

        if model == "era":

            #            from input_era import open_era

            indat = input_era.open_era(filename, **kwargs)

        elif model == "icon":
            #            from input_icon import open_icon

            indat = input_icon.open_icon(filename, **kwargs)

        elif model == "nextgems":
            #            from input_icon import open_icon

            catname = filename
            indat = input_nextgems.open_nextgems(catname, **kwargs)

        if isel is not None:
            self.input_data = indat.isel(**isel)
        else:
            self.input_data = indat

        stacked_input_data = self.input_data.stack(profile=profile_dimensions)
        total_number_of_profiles = len(stacked_input_data.profile)

        self.input_data_as_profile = stacked_input_data

        self.total_number_of_profiles = total_number_of_profiles

        return

    def data2profile(self, **kwargs):
        """
        Converts data to a profile object.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        myProfiles : pyrttov.Profiles
            The profile object.
        
        Notes
        - The following variables are expected in the input_data:
        ------------------------------------------------------------------
        - p
        - t
        - q
        - lon
        - lat
        - SKT
        - SP
        - T2M
        - clwc
        - ciwc
        - cc
        - The following aspects need to be considered:
        ------------------------------------------------------------------
        - geometry
        - q2m
        - time
        """

        # arguments handling
        if "synsat_snow_factor" in kwargs:
            use_snow_factor = True
            snow_factor = kwargs["synsat_snow_factor"]
        else:
            use_snow_factor = False

        # get all stacked data
        stacked_input_data = self.input_data_as_profile

        if "isel" in kwargs:
            isel = kwargs["isel"]
        else:
            isel = {"profile": slice(0, None)}

        profs = stacked_input_data.isel(**isel).load()

        # initialize profile
        nlevels = profs.dims["lev"]
        nprofiles = profs.dims["profile"]
        myProfiles = pyrttov.Profiles(nprofiles, nlevels)

        # some util vars
        zeros = np.zeros_like(profs["p"].data.T)
        ones = zeros[:, :1] + 1

        
        # fill profile
        q = profs["q"].data.T
        Temp =  profs["t"].data.T

        Temp = np.clip(Temp, 100, 400) 

        myProfiles.P = profs["p"].data.T * 1e-2  # in hPa
        myProfiles.T = Temp # gas_units = 1 => kg/kg over moist air (default)
        myProfiles.Q = q

        # get satellite angles
        lon, lat = profs["lon"].data, profs["lat"].data
        azi, zen = lonlat2azizen(lon, lat)

        # set max zen angle
        zen = np.clip(zen, 0, 80)

        sunazi, sunzen = zeros[:, :1], zeros[:, :1]

        myProfiles.Angles = np.vstack([zen, azi, 0 * zen, 0 * azi]).T    # (zenangle, azangle, sunzenangle, sunazangle) 
        myProfiles.SurfGeom = np.vstack([lat, lon,  0 * lat]).T           # (latitude, longitude, elevation) for each profile.
        myProfiles.SurfType = zeros[:, :2]

        skt = np.expand_dims(profs["SKT"], axis=1)
        fastem = np.hstack([3 * ones, 5 * ones, 15 * ones, 0.1 * ones, 0.3 * ones])

        myProfiles.Skin = np.hstack([skt, zeros[:, :3], fastem])

        ps2m = np.expand_dims(profs["SP"], axis=1) * 1e-2  # in hPa
        T2m = np.expand_dims(profs["T2M"], axis=1)

        q2m = np.expand_dims(q[:, 0], axis=1)  # only dew point there

        myProfiles.S2m = np.hstack([ps2m, T2m, q2m, zeros[:, :3]])

        tvec = dt2cal(profs.time.data[0])
        tvec = np.expand_dims(tvec, axis=0)[:, :6]
        myProfiles.DateTimes = tvec.repeat(nprofiles, axis=0)

        # testing the cloud vars here
        # myProfiles.Ngases = 4
        q = profs["q"].data.T
        qc = profs["clwc"].data.T

        qi = profs["ciwc"].data.T

        if use_snow_factor:
            print("... [synsat]: applying snow factor,", snow_factor)
            qs = profs["cswc"].data.T
            q_frozen = qi + snow_factor * qs
        else:
            q_frozen = qi

        cc = profs["cc"].data.T

        gases = np.stack([q, cc, qc, q_frozen])
        myProfiles.MmrCldAer = 1
        myProfiles.Gases = gases
        myProfiles.GasId = np.array([1, 20, 21, 30])

        # this is Baum + McFarquhar
        myProfiles.IceCloud = np.hstack(
            [
                1 * ones,
                4 * ones,
            ]
        )

        return myProfiles
