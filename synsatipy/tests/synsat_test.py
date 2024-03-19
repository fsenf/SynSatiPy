#!/usr/bin/env python

import numpy as np

from synsatipy.starter import pyrttov

from synsatipy.synsat import SynSatBase


class SynSatTest(SynSatBase):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.load_example_data()

        return

    def load_example_data(self):

        import example_data as ex

        # Declare an instance of Profiles
        nlevels = len(ex.p_ex)
        nprofiles = 8
        myProfiles = pyrttov.Profiles(nprofiles, nlevels)

        # Associate the profiles and other data from example_data.h with myProfiles
        # Note that the simplecloud, clwscheme, icecloud and zeeman data are not mandatory and
        # are omitted here

        def expand2nprofiles(n, nprof):
            """Transform 1D array to a [nprof, nlevels] array"""
            outp = np.empty((nprof, len(n)), dtype=n.dtype)
            for i in range(nprof):
                outp[i, :] = n[:]
            return outp

        myProfiles.GasUnits = ex.gas_units
        myProfiles.P = expand2nprofiles(ex.p_ex, nprofiles)
        myProfiles.T = expand2nprofiles(ex.t_ex, nprofiles)
        # Modify the temperature of the second profile

        for i in range(nprofiles):
            myProfiles.T[i, :] += i
        myProfiles.Q = expand2nprofiles(ex.q_ex, nprofiles)
        myProfiles.CO2 = expand2nprofiles(ex.co2_ex, nprofiles)

        myProfiles.Angles = expand2nprofiles(ex.angles[0], nprofiles)
        myProfiles.S2m = expand2nprofiles(ex.s2m[0], nprofiles)
        myProfiles.Skin = expand2nprofiles(ex.skin[0], nprofiles)
        myProfiles.SurfType = expand2nprofiles(ex.surftype[0], nprofiles)
        myProfiles.SurfGeom = expand2nprofiles(ex.surfgeom[0], nprofiles)
        myProfiles.DateTimes = expand2nprofiles(ex.datetimes[0], nprofiles)

        self.Profiles = myProfiles
        print("... [synsat] example data loaded")

        attr = self.synsat
        attr.nprofiles = nprofiles
        return
