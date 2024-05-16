#!/usr/bin/env python

import sys
import numpy as np
import xarray as xr

from synsatipy.starter import pyrttov, __rttov_version__
import synsatipy.data_handler as data_handler
import synsatipy.output as output


class attributes:
    """ """

    pass


class synsat_attributes:
    """ """

    synsat = attributes()
    atlas = attributes()
    pass


class SynSatBase(pyrttov.Rttov, synsat_attributes):
    """Class for calculating MSG Synsats.

    The is a child class of pyrttov.Rttov.

    Notes
    =====

    General Notes on the Workflow:
    1. Options need to be provided
    2. Instrument (MSG-SEVIRI) is loaded
    3. Data needs to be read
    4. Atlasses are loaded (depend on time coordinate in data)
    5. RTTOV is called

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, *args, **kwargs):
        """
        Only added optional parameters are listed.

        Convertion: key should start with "synsat_{keywordname}"
        """

        # first, extract all specific optional arguments
        synsat_kwargs = {}
        keylist = kwargs.copy().keys()

        for keyname in keylist:
            if "synsat_" in keyname:
                synsat_kwargs[keyname] = kwargs.pop(keyname)

        # write keywords to attributes
        attr = self.synsat
        attr.atlasses_loaded = False
        attr.kwargs = synsat_kwargs

        # locate itself
        pyrttov_path = pyrttov.__path__[0]
        rttov_install_dir = "/".join(pyrttov_path.split("/")[:-2])

        attr.rttov_install_dir = rttov_install_dir

        attr.rttov_version = __rttov_version__

        # inheritate all important methods & attributes
        super().__init__(*args, **kwargs)

        # set default options
        self.set_default_options(**synsat_kwargs)

        # init field
        self.synsat.chunked_result = []

        # load msg
        self.load_msg(**synsat_kwargs)

        return

    def set_default_options(self, **synsat_kwargs):
        """

        Parameters
        ----------
        **synsat_kwargs :


        Returns
        -------

        """

        self.Options.AddInterp = True
        self.Options.AddSolar = True
        self.Options.AddClouds = True
        self.Options.VerboseWrapper = True

        self.synsat.nprofiles = None

        return

    def load_msg(self, synsat_msg_number=3, **synsat_kwargs):
        """

        Parameters
        ----------
        synsat_msg_number :
             (Default value = 3)
        **synsat_kwargs :


        Returns
        -------

        """

        # SEVIRI specifics
        # ================
        seviri_allchannel_names = [
            "vis006",
            "vis008",
            "nir016",
            "ir039" "wv062",
            "wv073",
            "ir087",
            "ir097",
            "ir108",
            "ir120",
            "ir134",
            "hrv",
        ]
        seviri_var_names = [
            "rho006",
            "rho008",
            "rho016",
            "bt039",
            "bt062",
            "bt073",
            "bt087",
            "bt097",
            "bt108",
            "bt120",
            "bt134",
            "rhohrv",
        ]

        seviri_var_units = (
            3
            * [
                "-",
            ]
            + 8
            * [
                "K",
            ]
            + ["-"]
        )

        # MSG options
        # ===========
        # For SEVIRI exclude ozone and hi-res vis channels (9 and 12) in this
        # example
        # chan_list_seviri = (1, 2, 3, 4, 5, 6, 7, 9, 10, 11)

        default_chan_list = (5, 6, 7, 9, 10, 11)
        chan_list_seviri = synsat_kwargs.get("synsat_channel_list", default_chan_list)

        attr = self.synsat

        chan_index = np.array(chan_list_seviri) - 1

        attr.channels = np.array(seviri_var_names)[chan_index]
        attr.units = np.array(seviri_var_units)[chan_index]
        nchan_seviri = len(chan_list_seviri)

        # check if solar channel are included
        attr.solar_calculations = np.any(np.array(chan_list_seviri) < 5)

        # Set the options for each Rttov instance:
        # - the path to the coefficient file must always be specified
        # - turn RTTOV interpolation on (because input pressure levels differ from
        #   coefficient file levels)
        # - set the verbose_wrapper flag to true so the wrapper provides more
        #   information
        # - enable solar simulations for SEVIRI
        # - enable CO2 simulations for HIRS (the CO2 profiles are ignored for
        #   the SEVIRI and MHS simulations)
        # - enable the store_trans wrapper option for MHS to provide access to
        #   RTTOV transmission structure

        # Add cloud opt. props file
        cldaer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/sccldcoef_msg_{synsat_msg_number}_seviri.dat"
        self.FileSccld = cldaer_filename
        print(f"... [synsat] set cloud / aerosol file to  {cldaer_filename}")

        coef_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/rttov13pred54L/rtcoef_msg_{synsat_msg_number}_seviri_o3.dat"
        self.FileCoef = coef_filename
        print(f"... [synsat] load coefficient file {coef_filename}")

        # save vars to attributes
        attr.chan_list_seviri = chan_list_seviri
        attr.nchan_seviri = nchan_seviri
        attr.coef_filename = coef_filename

        # Load the instruments: for HIRS and MHS do not supply a channel list and
        # so read all channels
        try:
            self.loadInst(chan_list_seviri)
        except self.RttovError as e:
            sys.stderr.write("Error loading instrument(s): {!s}".format(e))
            sys.exit(1)

        return

    def load_atlasses(self, synsat_default_month=8, **kwargs):
        """

        Parameters
        ----------
        synsat_default_month :
             (Default value = 8)
        **kwargs :


        Returns
        -------

        """

        # ------------------------------------------------------------------------
        # Load the emissivity and BRDF atlases
        # ------------------------------------------------------------------------

        # Load the emissivity and BRDF atlases:
        # - load data for the month in the profile data
        # - load the IR emissivity atlas data for multiple instruments so it can be used for SEVIRI and HIRS
        # - SEVIRI is the only VIS/NIR instrument we can use the single-instrument initialisation for the BRDF atlas

        attr = self.synsat

        if (
            attr.atlasses_loaded
            and attr.atlasses_initialied_for_nprofiles == attr.nprofiles
        ):

            print(f"... [synsat] atlasses are already loaded")
            return

        if not attr.nprofiles is None:
            # WARNING: this assumes that first month is representative for all profiles
            synsat_month = self.Profiles.DateTimes[0, 1]
        else:
            synsat_month = synsat_default_month

        irAtlas = pyrttov.Atlas()
        irAtlas.AtlasPath = "{}/{}".format(attr.rttov_install_dir, "emis_data")
        irAtlas.loadIrEmisAtlas(
            synsat_month, ang_corr=True
        )  # Include angular correction, but do not initialise for single-instrument

        if attr.solar_calculations:
            brdfAtlas = pyrttov.Atlas()
            brdfAtlas.AtlasPath = "{}/{}".format(attr.rttov_install_dir, "brdf_data")
            brdfAtlas.loadBrdfAtlas(
                synsat_month, self
            )  # Supply Rttov object to enable single-instrument initialisation
            brdfAtlas.IncSea = False  # Do not use BRDF atlas for sea surface types

            # Set up the surface emissivity/reflectance arrays and associate with the Rttov objects

        if attr.rttov_version >= 13.2:
            nemis_classes = 5
        else:
            nemis_classes = 4

        surfemisrefl_seviri = np.zeros(
            (nemis_classes, attr.nprofiles, attr.nchan_seviri), dtype=np.float64
        )

        self.SurfEmisRefl = surfemisrefl_seviri

        # Surface emissivity/reflectance arrays must be initialised *before every call to RTTOV*
        # Negative values will cause RTTOV to supply emissivity/BRDF values (i.e. equivalent to
        # calcemis/calcrefl TRUE - see RTTOV user guide)
        surfemisrefl_seviri[:, :, :] = -1.0

        # Call emissivity and BRDF atlases
        try:
            # Do not supply a channel list for SEVIRI: this returns emissivity/BRDF values for all
            # *loaded* channels which is what is required
            surfemisrefl_seviri[0, :, :] = irAtlas.getEmisBrdf(self)

            if attr.solar_calculations:
                surfemisrefl_seviri[1, :, :] = brdfAtlas.getEmisBrdf(self)

        except pyrttov.RttovError as e:
            # If there was an error the emissivities/BRDFs will not have been modified so it
            # is OK to continue and call RTTOV with calcemis/calcrefl set to TRUE everywhere
            sys.stderr.write("Error calling atlas: {!s}".format(e))

        attr.atlasses_loaded = True
        attr.atlasses_initialied_for_nprofiles = attr.nprofiles

        return

    def run_workflow(self, **kwargs):
        """

        Parameters
        ----------
        test :
             (Default value = True)
        **kwargs :


        Returns
        -------

        """

        # load example data
        if self.synsat.nprofiles is None:
            raise Exception("... [synsat] ERROR: no data loaded")

        # prepare & load atlasses
        self.load_atlasses(**kwargs)

        # run RTTOV
        self.runDirect()

        return


class SynSat(SynSatBase):
    def __init__(self, *args, **kwargs):

        # inheritate all important methods & attributes
        super().__init__(*args, **kwargs)

    def load(self, inputfile_or_data, **kwargs):

        model = kwargs.get("model", "auto")

        # use data handler to load data
        sdat = data_handler.DataHandler(model=model)

        # check if file or dataset is provided
        if type(inputfile_or_data) == type(""):

            inputfile = inputfile_or_data
            print(f"... [synsat] read data from file  {inputfile}")

            self.synsat.input_filename = inputfile

            sdat.open_data(inputfile, **kwargs)

        elif type(inputfile_or_data) == type(xr.Dataset()):
            sdat.input_data = inputfile_or_data

        self.synsat.data_handler = sdat

        return

    def chunked_run(self, **kwargs):

        # transform input data into profiles
        sdat = self.synsat.data_handler

        profs = sdat.data2profile(**kwargs)

        # forward profiles to RTTOV
        self.Profiles = profs
        self.synsat.nprofiles = profs.Nprofiles

        # and run workflow
        self.run_workflow()

        self.synsat.chunked_result += [self.BtRefl]


    def run(self, **kwargs):

        if "chunked" not in kwargs:
            isel = {"profile": slice(0, None)}
            self.chunked_run(isel=isel, **kwargs)

        else:
            sdat = self.synsat.data_handler

            ntot = sdat.total_number_of_profiles
            nprof_per_call = self.Options.NprofsPerCall

            if np.mod(ntot, nprof_per_call) == 0:
                residual = 0
            else:
                residual = 1

            nchunks = ntot // nprof_per_call + residual

            for ichunks in range(nchunks):

                prof0 = ichunks * nprof_per_call
                prof1 = (ichunks + 1) * nprof_per_call

                if prof1 >= ntot:
                    prof1 = None
                isel = {"profile": slice(prof0, prof1)}

                print(f"... [synsat] running {ichunks}/{nchunks} chunk with", isel)
                self.chunked_run(isel=isel, **kwargs)

        self.synsat.result = np.row_stack( self.synsat.chunked_result )


    def extract_output(self):

        attr = self.synsat

        # prepare a channels dataset
        channels = xr.DataArray(
            data=np.array(attr.channels),
            dims=[
                "channel",
            ],
        )

        # trick: we use input data to start output data
        indat = attr.data_handler.input_data_as_profile
        alldat = indat.assign_coords({"channel": channels})

        btrefl = xr.DataArray(data=self.synsat.result, coords=[alldat.profile, alldat.channel])
        alldat["btrefl"] = btrefl

        btrefl = alldat["btrefl"].unstack()

        synsat = alldat[[]]
        for ichan, chan_name in enumerate(btrefl.channel.data):

            # set data
            synsat[chan_name] = btrefl.sel(channel=chan_name)

            # also set meta data
            a = {}
            a["units"] = attr.units[ichan]
            a["long_name"] = "Synsat SEVIRI Brightness Temperature at %.1f um" % (
                np.float32(chan_name[2:]) / 10.0
            )

            synsat[chan_name].attrs = a

        del synsat.coords["channel"]

        attr.output = synsat

        # try to write global attrs
        if True: #try:
            synsat.attrs = output.prepare_global_attrs()
            synsat.attrs["input_filename"] = attr.input_filename

        else: #except:
            print("... [synsat]: WARNING: fail to write global attributes")

        self.synsat.output_data = synsat

        return synsat

    def save(self, output_filename):

        out = self.extract_output()

        print(f"... [synsat] write synsat data to {output_filename}")
        out.to_netcdf(output_filename)

        return
