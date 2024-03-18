#!/usr/bin/env python


import numpy as np
import datetime
import xarray as xr


from starter import pyrttov

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


def lonlat2azizen(lon, lat):

    # DESCRIPTION
    # ===========
    # calculates satellite zenith and azimuth given lon / lat
    # ====================================================================

    # satellite height and earth radius ..................................
    H = 42164
    R = 6378
    pi = np.pi

    # from degree to radiant .............................................
    lon, lat = np.deg2rad(lon), np.deg2rad(lat)

    # calculate angle on great circle between pixel and (0,0) ............
    delta = np.arccos(np.cos(lat) * np.cos(lon))

    # azimuth angle ......................................................
    azi = np.arccos(np.sin(lat) / np.sin(delta))

    # missing side of triangle ...........................................
    D = np.sqrt(R**2 + H**2 - 2 * H * R * np.cos(delta))

    # angle in the triangle on the opposite side of the height of satellite
    # angle larger than 90 deg -> use second argument of sine
    gamma = pi - np.arcsin(H / D * np.sin(delta))

    # zenith angle .......................................................
    zen = pi - gamma

    return np.rad2deg(azi), np.rad2deg(zen)


######################################################################
######################################################################


class DataHandler(object):
    def __init__(self, model="era", return_profile=True, **kwargs):

        self.model = model

        return

    def open_data(
        self,
        filename,
        **kwargs
    ):

        if self.model == "era":

            from input_era import open_era

            self.input_data = open_era(filename, **kwargs)

        elif self.model == "icon":
            from input_icon import open_icon

            self.input_data = open_icon(filename, **kwargs)

        return

    def data2profile(self):
        """
        TODO
        ====
        - geometry
        - q2m
        - time
        """

        # stack all together into profiles
        sdat = self.input_data
        profs = sdat.stack(profile=["time", "lon", "lat"])
        self.input_data_as_profile = profs

        # initialize profile
        nlevels = profs.dims["lev"]
        nprofiles = profs.dims["profile"]
        myProfiles = pyrttov.Profiles(nprofiles, nlevels)

        # some util vars
        zeros = np.zeros_like(profs["p"].data.T)
        ones = zeros[:, :1] + 1

        # fill profile
        q = profs["q"].data.T
        myProfiles.P = profs["p"].data.T * 1e-2  # in hPa
        myProfiles.T = profs[
            "t"
        ].data.T  # gas_units = 1 => kg/kg over moist air (default)
        myProfiles.Q = q

        # get satellite angles
        lon, lat = profs["lon"].data, profs["lat"].data
        azi, zen = lonlat2azizen(lon, lat)

        sunazi, sunzen = zeros[:, :1], zeros[:, :1]

        myProfiles.Angles = np.vstack([zen, azi, 0 * zen, 0 * azi]).T
        myProfiles.SurfGeom = np.vstack([lon, lat, 0 * lat]).T
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
        cc = profs["cc"].data.T

        gases = np.stack([q, cc, qc, qi])
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
