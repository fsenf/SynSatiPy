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

        # aerosol options
        use_aerosols = synsat_kwargs.get("synsat_use_aerosols", False)
        self.Options.AddAerosl = use_aerosols
        self.synsat.use_aerosols = use_aerosols

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

        implemented_instruments = ["seviri", "abi", "fci", "modis"]

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

        elif instrument == "modis":
            # Load EOS-MODIS configuration
            self.load_eos_modis(**synsat_kwargs)

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

        # Add aerosol file if enabled
        if attr.use_aerosols:
            aer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/scaercoef_msg_{synsat_msg_number}_seviri_cams.dat"
            self.FileScaer = aer_filename
            print(f"... [synsat] set aerosol file to {aer_filename}")

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
            "ch01",  # 0.47 μm - Blue
            "ch02",  # 0.64 μm - Red
            "ch03",  # 0.86 μm - Veggie
            "ch04",  # 1.37 μm - Cirrus
            "ch05",  # 1.6 μm - Snow/Ice
            "ch06",  # 2.2 μm - Cloud Particle Size
            "ch07",  # 3.9 μm - Shortwave Window
            "ch08",  # 6.2 μm - Upper-Level Water Vapor
            "ch09",  # 6.9 μm - Mid-Level Water Vapor
            "ch10",  # 7.3 μm - Lower-Level Water Vapor
            "ch11",  # 8.4 μm - Cloud-Top Phase
            "ch12",  # 9.6 μm - Ozone
            "ch13",  # 10.3 μm - Clean IR Longwave Window
            "ch14",  # 11.2 μm - IR Longwave Window
            "ch15",  # 12.3 μm - Dirty Longwave Window
            "ch16",  # 13.3 μm - CO2 Longwave
        ]
        abi_var_names = [
            "rho047",  # Reflectivity channels (1-6)
            "rho064",
            "rho086",
            "rho137",
            "rho160",
            "rho220",
            "bt039",  # Brightness temperature channels (7-16)
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

        abi_var_units = 6 * [
            "-",
        ] + 10 * [
            "K",
        ]

        # GOES-ABI options
        # ===========
        # Default to IR channels (channels 7-16)
        default_chan_list = (7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
        chan_list_instrument = synsat_kwargs.get(
            "synsat_channel_list", default_chan_list
        )

        attr = self.synsat
        attr.instrument = "ABI"

        subsatellite_lon = synsat_kwargs.get("synsat_subsatellite_lon", -75.2)
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

        if attr.use_aerosols:
            aer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/scaercoef_goes_{synsat_goes_number}_abi_cams.dat"
            self.FileScaer = aer_filename
            print(f"... [synsat] set aerosol file to {aer_filename}")

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
            "vis04",  # 0.444 μm - Blue
            "vis05",  # 0.510 μm - Green
            "vis06",  # 0.640 μm - Red
            "vis08",  # 0.865 μm - Vegetation Red Edge
            "vis09",  # 0.914 μm - Water Vapour
            "nir13",  # 1.375 μm - Cirrus
            "nir16",  # 1.610 μm - Snow/Ice/Cloud Phase
            "nir22",  # 2.250 μm - Aerosol/Cloud Particle Size
            "ir38",  # 3.80 μm - Hot objects/Fire/Night microphysics
            "wv63",  # 6.25 μm - Upper-Level Water Vapour
            "wv73",  # 7.35 μm - Lower-Level Water Vapour
            "ir87",  # 8.70 μm - Cloud Phase/SO2
            "ir97",  # 9.66 μm - Ozone
            "ir105",  # 10.50 μm - Clean IR Window
            "ir123",  # 12.30 μm - Dirty IR Window
            "ir133",  # 13.30 μm - CO2
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
            "bt038",  # Brightness temperature channels (8-16)
            "bt063",
            "bt073",
            "bt087",
            "bt097",
            "bt105",
            "bt123",
            "bt133",
        ]
        fci_var_units = 8 * [
            "-",
        ] + 8 * [
            "K",
        ]

        # MTG-FCI options
        # ===========
        # Default to IR and water vapor channels (channels 9-16)
        default_chan_list = (9, 10, 11, 12, 13, 14, 15, 16)
        chan_list_instrument = synsat_kwargs.get(
            "synsat_channel_list", default_chan_list
        )

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

        # Add aerosol file if enabled
        if attr.use_aerosols:
            aer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/scaercoef_mtg_{synsat_mtg_number}_fci_cams.dat"
            self.FileScaer = aer_filename
            print(f"... [synsat] set aerosol file to {aer_filename}")

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

    def load_eos_modis(self, synsat_modis_satellite="terra", **synsat_kwargs):
        """
        Loads configuration specific for the EOS-MODIS instrument.

        Parameters
        ----------
        synsat_modis_satellite : str
            EOS satellite name, either 'terra' (EOS-1) or 'aqua' (EOS-2).
            (Default value = 'terra')
        **synsat_kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """

        # Map satellite name to EOS number
        satellite_map = {"terra": 1, "aqua": 2}
        satellite_name = synsat_kwargs.get(
            "synsat_modis_satellite", synsat_modis_satellite
        ).lower()
        if satellite_name not in satellite_map:
            raise ValueError(
                f"Unknown MODIS satellite '{satellite_name}'. "
                f"Supported values are: {list(satellite_map.keys())}"
            )
        eos_number = satellite_map[satellite_name]

        # MODIS channel definitions (bands 1-36)
        # Bands 1-19: reflective solar (VIS/NIR, 0.4-2.2 µm)
        # Bands 20-36: thermal emissive (3.7-14.4 µm), except band 26 (1.38 µm, solar)
        modis_var_names = [
            # rho: centre_µm × 100, 3-digit zero-padded
            "rho064",  #  1 - 620-670 nm   (0.645µm → 64)
            "rho086",  #  2 - 841-876 nm   (0.859µm → 86)
            "rho047",  #  3 - 459-479 nm   (0.469µm → 47)
            "rho056",  #  4 - 545-565 nm   (0.555µm → 56)
            "rho124",  #  5 - 1230-1250 nm (1.240µm → 124)
            "rho164",  #  6 - 1628-1652 nm (1.640µm → 164)
            "rho213",  #  7 - 2105-2155 nm (2.130µm → 213)
            "rho041",  #  8 - 405-420 nm   (0.413µm → 41)
            "rho044",  #  9 - 438-448 nm   (0.443µm → 44)
            "rho046",  # 10 - 438-493 nm   (0.466µm → 46, floor to avoid clash with band 3)
            "rho053",  # 11 - 526-536 nm   (0.531µm → 53)
            "rho055",  # 12 - 546-556 nm   (0.551µm → 55)
            "rho067",  # 13 - 662-672 nm   (0.667µm → 67)
            "rho068",  # 14 - 673-683 nm   (0.678µm → 68)
            "rho075",  # 15 - 743-753 nm   (0.748µm → 75)
            "rho087",  # 16 - 862-877 nm   (0.870µm → 87)
            "rho091",  # 17 - 890-920 nm   (0.905µm → 91)
            "rho093",  # 18 - 931-941 nm   (0.936µm → 93, floor to avoid clash with band 19)
            "rho094",  # 19 - 915-965 nm   (0.940µm → 94)
            # bt: centre_µm × 10, 3-digit zero-padded
            "bt038",  # 20 - 3.660-3.840 µm (3.750µm → 038)
            "bt039",  # 21 - 3.929-3.989 µm (fire channel; floor to avoid clash with band 22)
            "bt040",  # 22 - 3.929-3.989 µm (3.959µm → 040)
            "bt041",  # 23 - 4.020-4.080 µm (4.050µm → 041)
            "bt045",  # 24 - 4.433-4.498 µm (4.466µm → 045)
            "bt046",  # 25 - 4.482-4.549 µm (4.516µm → 046, ceil to avoid clash with band 24)
            "rho138",  # 26 - 1.360-1.390 µm (1.375µm → 138, cirrus solar channel)
            "bt067",  # 27 - 6.535-6.895 µm (6.715µm → 067)
            "bt073",  # 28 - 7.175-7.475 µm (7.325µm → 073)
            "bt086",  # 29 - 8.400-8.700 µm (8.550µm → 086)
            "bt097",  # 30 - 9.580-9.880 µm (9.730µm → 097, ozone)
            "bt110",  # 31 - 10.780-11.280 µm (11.030µm → 110)
            "bt120",  # 32 - 11.770-12.270 µm (12.020µm → 120)
            "bt133",  # 33 - 13.185-13.485 µm (13.335µm → 133)
            "bt136",  # 34 - 13.485-13.785 µm (13.635µm → 136)
            "bt139",  # 35 - 13.785-14.085 µm (13.935µm → 139)
            "bt142",  # 36 - 14.085-14.385 µm (14.235µm → 142)
        ]

        modis_var_units = (
            19 * ["-"]  # bands 1-19: reflective
            + 6 * ["K"]  # bands 20-25: thermal
            + ["-"]  # band  26: solar (cirrus)
            + 9 * ["K"]  # bands 27-36: thermal
        )

        # Default channel list: key thermal/WV bands analogous to other instruments
        default_chan_list = (20, 22, 27, 28, 29, 31, 32, 33)
        chan_list_instrument = synsat_kwargs.get(
            "synsat_channel_list", default_chan_list
        )

        attr = self.synsat
        attr.instrument = f"MODIS ({satellite_name.capitalize()})"

        # MODIS is polar-orbiting — subsatellite_lon is not physically meaningful
        # but kept as a dummy for interface compatibility
        subsatellite_lon = synsat_kwargs.get("synsat_subsatellite_lon", None)
        attr.subsatellite_lon = subsatellite_lon

        chan_index = np.array(chan_list_instrument) - 1

        attr.channels = np.array(modis_var_names)[chan_index]
        attr.units = np.array(modis_var_units)[chan_index]
        nchan_instrument = len(chan_list_instrument)

        # Solar channels: bands 1-19 are always solar; band 26 (index 25) is also solar
        solar_indices = set(range(1, 20)) | {26}
        attr.solar_calculations = any(
            ch in solar_indices for ch in chan_list_instrument
        )

        # Coefficient files
        cldaer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/sccldcoef_eos_{eos_number}_modis.dat"
        self.FileSccld = cldaer_filename
        print(f"... [synsat] set cloud file to {cldaer_filename}")

        if attr.use_aerosols:
            aer_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/cldaer_visir/scaercoef_eos_{eos_number}_modis_cams.dat"
            self.FileScaer = aer_filename
            print(f"... [synsat] set aerosol file to {aer_filename}")

        coef_filename = f"{attr.rttov_install_dir}/rtcoef_rttov13/rttov13pred54L/rtcoef_eos_{eos_number}_modis_o3.dat"
        self.FileCoef = coef_filename
        print(f"... [synsat] load coefficient file {coef_filename}")

        # Save vars to attributes
        attr.chan_list_instrument = chan_list_instrument
        attr.nchan_instrument = nchan_instrument
        attr.coef_filename = coef_filename

        # Load the instrument
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

        except self.RttovError as e:
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
        aerosol_config = kwargs.get('aerosol_config', {})

        attr = self.synsat
        lon0 = attr.subsatellite_lon
        use_aerosols = attr.use_aerosols

        # use data handler to load data
        sdat = data_handler.DataHandler(model=model, use_aerosols=use_aerosols, aerosol_config=aerosol_config)

        # check if file or dataset is provided
        if type(inputfile_or_data) == type(""):

            inputfile = inputfile_or_data
            print(f"... [synsat] read data from file  {inputfile}")

            self.synsat.input_filename = inputfile

            sdat.open_data(inputfile, lon0=lon0, use_aerosols=use_aerosols, **kwargs)

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

        profs = sdat.data2profile(lon0=lon0, **kwargs)

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
        full_result = np.full(
            (original_stacked.sizes["profile"], len(attr.channels)), np.nan
        )

        # Fill in the results at the correct positions
        full_result[selected_indices, :] = self.synsat.result

        # Create the DataArray with full coordinates AND attributes preserved
        channels = xr.DataArray(data=np.array(attr.channels), dims=["channel"])

        btrefl_full = xr.DataArray(
            data=full_result,
            coords={"profile": original_stacked.profile, "channel": channels},
            dims=["profile", "channel"],
            attrs=original_stacked.attrs,  # Preserve dataset-level attributes if needed
        )

        # Copy coordinate attributes from original stacked data
        for coord_name in original_stacked.coords:
            if coord_name in btrefl_full.coords:
                btrefl_full.coords[coord_name].attrs = original_stacked.coords[
                    coord_name
                ].attrs

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
                np.float32(chan_name[2:]) / 10.0,
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
