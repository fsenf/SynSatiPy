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
    -----


    General Notes on the Workflow:
    1. Options need to be provided
    2. Instrument (MSG-SEVIRI) is loaded
    3. Data needs to be read
    4. Atlasses are loaded (depend on time coordinate in data)
    5. RTTOV is called



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

        # load instrument based on specified instrument
        self.load_instrument(**synsat_kwargs)

        return

    def set_default_options(self, **synsat_kwargs):
        """
        Sets default options for the RTTOV wrapper.


        Parameters
        ----------
        **synsat_kwargs : dict
            Additional keyword arguments.


        Returns
        -------
        None

        """

        self.Options.AddInterp = True
        self.Options.AddSolar = True
        self.Options.AddClouds = True
        self.Options.VerboseWrapper = True

        self.synsat.nprofiles = None

        return

    def load_instrument(self, **synsat_kwargs):
        """
        Loads the specified instrument configuration.

        Parameters
        ----------
        **synsat_kwargs : dict
            Additional keyword arguments including synsat_instrument.

        Returns
        -------
        None
        """

        implemented_instruments = ["seviri", "abi", "fci"]


        # Default to SEVIRI if not specified
        instrument = synsat_kwargs.get("synsat_instrument", "seviri").lower()

        if instrument == "seviri":
            # Load SEVIRI configuration
            self.load_msg_seviri(**synsat_kwargs)

        elif instrument == "abi":
            # Load GOES-ABI configuration
            self.load_goes_abi(**synsat_kwargs)

        elif instrument == "fci":
            # Load MTG-FCI configuration
            self.load_mtg_fci(**synsat_kwargs)
        
        else:
            print(
                f"... [synsat] WARNING: {instrument} is not a valid instrument. "
                f"Supported instruments are: {', '.join(implemented_instruments)}"
            )
            # Raise an error if the instrument is not supported
            raise ValueError(f"Unsupported instrument: {instrument}")

        return

    def load_msg_seviri(self, synsat_msg_number=3, **synsat_kwargs):
        """
        Loads configuration specific for the MSG-SEVIRI instrument.

        Parameters
        ----------
        synsat_msg_number : int
            MSG number. (Default value = 3)
        **synsat_kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        # SEVIRI specifics
        # ================
        seviri_allchannel_names = [
            "vis006",
            "vis008",
            "nir016",
            "ir039",
            "wv062",
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
        attr.instrument = "SEVIRI"

        subsatellite_lon = synsat_kwargs.get("synsat_subsatellite_lon", 0.0)
        attr.subsatellite_lon = subsatellite_lon

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
        attr.chan_list_instrument = chan_list_seviri
        attr.nchan_instrument = nchan_seviri
        attr.coef_filename = coef_filename

        # Load the instruments: for HIRS and MHS do not supply a channel list and
        # so read all channels
        try:
            self.loadInst(chan_list_seviri)
        except self.RttovError as e:
            sys.stderr.write("Error loading instrument(s): {!s}".format(e))
            sys.exit(1)

        return

    def load_goes_abi(self, synsat_goes_number=16, **synsat_kwargs):
        """
        Loads configuration specific for the GOES-ABI instrument.

        Parameters
        ----------
        synsat_goes_number : int
            GOES satellite number. (Default value = 16)
        **synsat_kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        # ABI specifics
        # ================
        abi_allchannel_names = [
            "ch01",  # 0.47 µm - Blue
            "ch02",  # 0.64 µm - Red
            "ch03",  # 0.86 µm - Veggie
            "ch04",  # 1.37 µm - Cirrus
            "ch05",  # 1.6 µm - Snow/Ice
            "ch06",  # 2.2 µm - Cloud Particle Size
            "ch07",  # 3.9 µm - Shortwave Window
            "ch08",  # 6.2 µm - Upper-Level Water Vapor
            "ch09",  # 6.9 µm - Mid-Level Water Vapor
            "ch10",  # 7.3 µm - Lower-Level Water Vapor
            "ch11",  # 8.4 µm - Cloud-Top Phase
            "ch12",  # 9.6 µm - Ozone
            "ch13",  # 10.3 µm - Clean IR Longwave Window
            "ch14",  # 11.2 µm - IR Longwave Window
            "ch15",  # 12.3 µm - Dirty Longwave Window
            "ch16",  # 13.3 µm - CO2 Longwave
        ]
        abi_var_names = [
            "rho047",  # Reflectivity channels (1-6)
            "rho064",
            "rho086",
            "rho137",
            "rho160",
            "rho220",
            "bt039",   # Brightness temperature channels (7-16)
            "bt062",
            "bt069",
            "bt073",
            "bt084",
            "bt096",
            "bt103",
            "bt112",
            "bt123",
            "bt133",
        ]

        abi_var_units = (
            6 * ["-",] + 10 * ["K",]
        )

        # GOES-ABI options
        # ===========
        # Default to IR channels (channels 7-16)
        default_chan_list = (7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
        chan_list_instrument = synsat_kwargs.get("synsat_channel_list", default_chan_list)

        attr = self.synsat
        attr.instrument = "ABI"

        subsatellite_lon = synsat_kwargs.get("synsat_subsatellite_lon",  -75.2)
        attr.subsatellite_lon = subsatellite_lon

        chan_index = np.array(chan_list_instrument) - 1

        attr.channels = np.array(abi_var_names)[chan_index]
        attr.units = np.array(abi_var_units)[chan_index]
        nchan_instrument = len(chan_list_instrument)

        # check if solar channel are included
        attr.solar_calculations = np.any(np.array(chan_list_instrument) < 7)

        # Add cloud opt. props file
        cldaer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/sccldcoef_goes_{synsat_goes_number}_abi.dat"
        self.FileSccld = cldaer_filename
        print(f"... [synsat] set cloud / aerosol file to {cldaer_filename}")

        coef_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/rttov13pred54L/rtcoef_goes_{synsat_goes_number}_abi_o3.dat"
        self.FileCoef = coef_filename
        print(f"... [synsat] load coefficient file {coef_filename}")

        # save vars to attributes
        attr.chan_list_instrument = chan_list_instrument
        attr.nchan_instrument = nchan_instrument
        attr.coef_filename = coef_filename

        # Load the instruments
        try:
            self.loadInst(chan_list_instrument)
        except self.RttovError as e:
            sys.stderr.write("Error loading instrument(s): {!s}".format(e))
            sys.exit(1)

        return

    def load_mtg_fci(self, synsat_mtg_number=1, **synsat_kwargs):
        """
        Loads configuration specific for the MTG-FCI instrument.

        Parameters
        ----------
        synsat_mtg_number : int
            MTG satellite number. (Default value = 1)
        **synsat_kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        # FCI specifics
        # ================
        fci_allchannel_names = [
            "vis04",   # 0.444 µm - Blue
            "vis05",   # 0.510 µm - Green
            "vis06",   # 0.640 µm - Red
            "vis08",   # 0.865 µm - Vegetation Red Edge
            "vis09",   # 0.914 µm - Water Vapour
            "nir13",   # 1.375 µm - Cirrus
            "nir16",   # 1.610 µm - Snow/Ice/Cloud Phase
            "nir22",   # 2.250 µm - Aerosol/Cloud Particle Size
            "ir38",    # 3.80 µm - Hot objects/Fire/Night microphysics
            "wv63",    # 6.25 µm - Upper-Level Water Vapour
            "wv69",    # 6.95 µm - Mid-Level Water Vapour  
            "wv73",    # 7.35 µm - Lower-Level Water Vapour
            "ir87",    # 8.70 µm - Cloud Phase/SO2
            "ir97",    # 9.66 µm - Ozone
            "ir105",   # 10.50 µm - Clean IR Window
            "ir123",   # 12.30 µm - Dirty IR Window
            "ir133",   # 13.30 µm - CO2
        ]
        fci_var_names = [
            "rho044",  # Reflectivity channels (1-8)
            "rho051",
            "rho064",
            "rho087",
            "rho091",
            "rho138",
            "rho161",
            "rho225",
            "bt038",   # Brightness temperature channels (9-17)
            "bt063",
            "bt069",
            "bt073",
            "bt087",
            "bt097",
            "bt105",
            "bt123",
            "bt133",
        ]

        fci_var_units = (
            8 * ["-",] + 9 * ["K",]
        )

        # MTG-FCI options
        # ===========
        # Default to IR and water vapor channels (channels 9-17)
        default_chan_list = [9, 10, 11, 12, 13, 14, 15, 16, 17]
        chan_list_instrument = synsat_kwargs.get("synsat_channel_list", default_chan_list)

        attr = self.synsat
        attr.instrument = "FCI"

        subsatellite_lon = synsat_kwargs.get("synsat_subsatellite_lon", 0.0)
        attr.subsatellite_lon = subsatellite_lon

        chan_index = np.array(chan_list_instrument) - 1

        attr.channels = np.array(fci_var_names)[chan_index]
        attr.units = np.array(fci_var_units)[chan_index]
        nchan_instrument = len(chan_list_instrument)

        # check if solar channel are included
        attr.solar_calculations = np.any(np.array(chan_list_instrument) < 9)

        # Add cloud opt. props file
        cldaer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/sccldcoef_mtg_{synsat_mtg_number}_fci.dat"
        self.FileSccld = cldaer_filename
        print(f"... [synsat] set cloud / aerosol file to {cldaer_filename}")

        coef_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/rttov13pred54L/rtcoef_mtg_{synsat_mtg_number}_fci_o3.dat"
        self.FileCoef = coef_filename
        print(f"... [synsat] load coefficient file {coef_filename}")

        # save vars to attributes
        attr.chan_list_instrument = chan_list_instrument
        attr.nchan_instrument = nchan_instrument
        attr.coef_filename = coef_filename

        # Load the instruments
        try:
            self.loadInst(chan_list_instrument)
        except self.RttovError as e:
            sys.stderr.write("Error loading instrument(s): {!s}".format(e))
            sys.exit(1)

        return

    def load_atlasses(self, synsat_default_month=8, **kwargs):
        """
        Load the emissivity and BRDF atlases.

        Parameters
        ----------
        synsat_default_month : int
            Month to use for the emissivity and BRDF atlases.
           (Default value = 8)
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None

        """

        # ------------------------------------------------------------------------
        # Load the emissivity and BRDF atlases
        # ------------------------------------------------------------------------

        # Load the emissivity and BRDF atlases:
        # - load data for the month in the profile data
        # - load the IR emissivity atlas data for multiple instruments so it can be used for SEVIRI and HIRS
        # - SEVIRI is the only VIS/NIR instrument we can use the single-instrument initialisation for the BRDF atlas

        attr = self.synsat

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
            (nemis_classes, attr.nprofiles, attr.nchan_instrument), dtype=np.float64
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
        Run the full RTTOV workflow. This includes loading the atlasses, running RTTOV
        and extracting the output.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments


        Returns
        -------
        None

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
    """
    SynSat class for calculating MSG Synsats.

    The is a child class of SynSatBase.

    Notes
    -----
    This class is the main class for calculating MSG Synsats.

    Parameters
    ----------
    *args : list
        List of arguments passed to the parent class.

    **kwargs : dict
        Additional keyword arguments passed to the parent class.
    """

    def __init__(self, *args, **kwargs):

        # inheritate all important methods & attributes
        super().__init__(*args, **kwargs)

    def load(self, inputfile_or_data, **kwargs):
        """
        Load data from file or dataset.

        Parameters
        ----------
        inputfile_or_data : str or xr.Dataset
            The input file or dataset.

        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        model = kwargs.get("model", "auto")
        lon0 = self.synsat.subsatellite_lon

        # use data handler to load data
        sdat = data_handler.DataHandler(model=model)

        # check if file or dataset is provided
        if type(inputfile_or_data) == type(""):

            inputfile = inputfile_or_data
            print(f"... [synsat] read data from file  {inputfile}")

            self.synsat.input_filename = inputfile

            sdat.open_data(inputfile, lon0 = lon0, **kwargs)

        elif type(inputfile_or_data) == type(xr.Dataset()):
            sdat.input_data = inputfile_or_data

        sdat.stack_data_as_profile(**kwargs)

        self.synsat.data_handler = sdat

        return

    def chunked_run(self, **kwargs):
        """
        Runs a small chunk of the RTTOV workflow.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        # transform input data into profiles
        sdat = self.synsat.data_handler
        lon0 = self.synsat.subsatellite_lon

        profs = sdat.data2profile(lon0 = lon0, **kwargs)

        # forward profiles to RTTOV
        self.Profiles = profs
        self.synsat.nprofiles = profs.Nprofiles

        # and run workflow
        self.run_workflow()

        self.synsat.chunked_result += [self.BtRefl]

    def run(self, **kwargs):
        """
        Run the complete RTTOV workflow. This is a wrapper for the chunked_run method.

        Parameters
        ----------
        efficiency_factor : int, optional
            Multiplicative factor for the number of profiles processed per call when
            chunked processing is enabled (i.e., when 'chunked' is in kwargs).
            The actual number of profiles per chunk is calculated as
            efficiency_factor * NprofsPerCall. Default is 4.
        **kwargs : dict
            Additional keyword arguments. If 'chunked' is included in kwargs, the
            workflow will process data in chunks using the efficiency_factor parameter.

        Returns
        -------
        None

        """
        # init results field
        self.synsat.chunked_result = []

        if "chunked" not in kwargs:
            isel = {"profile": slice(0, None)}
            self.chunked_run(isel=isel, **kwargs)

        else:
            sdat = self.synsat.data_handler

            efficiency_factor = kwargs.get("efficiency_factor", 4)
            ntot = sdat.total_number_of_profiles
            nprof_per_call = efficiency_factor * self.Options.NprofsPerCall

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

        self.synsat.result = np.row_stack(self.synsat.chunked_result)

    def extract_output(self):
        """
        Extracts the output data from the RTTOV variables and prepares it for saving.
        """
        attr = self.synsat
        sdat = attr.data_handler

        # Get the original stacked data (before masking) for proper unstacking
        original_stacked = sdat.input_data.stack(profile=sdat.profile_dimensions)
        selected_indices = sdat.selected_profiles_index

        # Create a full-size result array filled with NaN
        full_result = np.full((original_stacked.sizes['profile'], len(attr.channels)), np.nan)
        
        # Fill in the results at the correct positions
        full_result[selected_indices, :] = self.synsat.result
        
        # Create the DataArray with full coordinates AND attributes preserved
        channels = xr.DataArray(data=np.array(attr.channels), dims=["channel"])

        btrefl_full = xr.DataArray(
            data=full_result, 
            coords={
                'profile': original_stacked.profile,
                'channel': channels
            },
            dims=['profile', 'channel'],
            attrs=original_stacked.attrs  # Preserve dataset-level attributes if needed
        )

        # Copy coordinate attributes from original stacked data
        for coord_name in original_stacked.coords:
            if coord_name in btrefl_full.coords:
                btrefl_full.coords[coord_name].attrs = original_stacked.coords[coord_name].attrs

        # Now unstack will work correctly and preserve coordinate attributes
        btrefl = btrefl_full.unstack()
        
        # Start with the original input data structure to preserve coordinate attributes
        synsat = xr.Dataset()

        # Add the satellite data while preserving coordinate attributes
        for ichan, chan_name in enumerate(btrefl.channel.data):
            # Set data
            synsat[chan_name] = btrefl.sel(channel=chan_name)

            # Set variable attributes (not coordinate attributes)
            a = {}
            a["units"] = attr.units[ichan]
            a["long_name"] = "Synsat %s Brightness Temperature at %.1f um" % (
                attr.instrument,
                np.float32(chan_name[2:]) / 10.0
            )
            synsat[chan_name].attrs = a

        del synsat.coords["channel"]

        # Write global attrs
        synsat.attrs = output.prepare_global_attrs()
        synsat.attrs["input_filename"] = attr.input_filename

        self.synsat.output_data = synsat

        return synsat

    def save(self, output_filename):
        """
        Save the output data to a netcdf file.

        Parameters
        ----------
        output_filename : str
            The output filename.

        Returns
        -------
        None

        """

        out = self.extract_output()

        print(f"... [synsat] write synsat data to {output_filename}")
        out.to_netcdf(output_filename)

        return
