#!/usr/bin/env python

import sys
import numpy as np
import xarray as xr

from starter import pyrttov
import data_handler


class attributes:
    """ """
    pass


class synsat_attributes:
    """ """
    synsat = attributes()
    atlas = attributes()
    pass


import pyrttov


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
        attr.kwargs = synsat_kwargs

        # locate itself
        pyrttov_path = pyrttov.__path__[0]
        rttov_install_dir = "/".join(pyrttov_path.split("/")[:-2])

        attr.rttov_install_dir = rttov_install_dir

        # inheritate all important methods & attributes
        super().__init__(*args, **kwargs)

        # set default options
        self.set_default_options(**synsat_kwargs)

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
        seviri_allchannel_names = [ 'vis006', 'vis008', 'nir016', 'ir039'
                                    'wv062',  'wv073', 
                                    'ir087', 'ir097', 'ir108', 'ir120', 'ir134', 
                                    'hrv']
        seviri_var_names = ['rho006', 'rho008', 'rho016', 'bt039', 
                            'bt062', 'bt073', 'bt087', 'bt097', 'bt108', 'bt120', 'bt134', 'rhohrv']

        seviri_var_units = 3*['-',] + 8*['K',] + ['-']


        # MSG options
        # ===========
        # For SEVIRI exclude ozone and hi-res vis channels (9 and 12) in this
        # example
        # chan_list_seviri = (1, 2, 3, 4, 5, 6, 7, 9, 10, 11)
 
        default_chan_list = (5, 6, 7, 9, 10, 11)
        chan_list_seviri = synsat_kwargs.get( 'synsat_channel_list', default_chan_list)

        attr = self.synsat

        chan_index = np.array( chan_list_seviri ) - 1
        
        attr.channels = np.array(seviri_var_names)[ chan_index ]
        attr.units    = np.array(seviri_var_units)[ chan_index ]
        nchan_seviri = len(chan_list_seviri)

        # check if solar channel are included
        attr.solar_calculations = np.any( np.array( chan_list_seviri ) < 5 )

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
        surfemisrefl_seviri = np.zeros(
                (4, attr.nprofiles, attr.nchan_seviri), dtype=np.float64
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


class SynSat( SynSatBase ):

    def __init__(self, *args, **kwargs):
        
        # inheritate all important methods & attributes
        super().__init__(*args, **kwargs)


    def load(self, inputfile ):

        # use data handler to load data
        sdat = data_handler.DataHandler()
        sdat.open_data( inputfile )

        self.synsat.data_handler = sdat
        profs = sdat.data2profile()

        # forward profiles to RTTOV
        self.Profiles = profs
        self.synsat.nprofiles = profs.Nprofiles

        return


    def run( self ):

        self.run_workflow()

    def extract_output( self ):

        attr = self.synsat

        # prepare a channels dataset
        channels = xr.DataArray(data =  np.array( attr.channels),
                                        dims = ['channel',])

        # trick: we use input data to start output data
        indat = attr.data_handler.input_data_as_profile
        alldat = indat.assign_coords({'channel': channels})

        btrefl = xr.DataArray( data = self.BtRefl, coords = [alldat.profile, alldat.channel])
        alldat['btrefl'] = btrefl


        btrefl = alldat['btrefl'].unstack()

        synsat = alldat[[]]
        for ichan, chan_name in enumerate(btrefl.channel.data):

            # set data
            synsat[chan_name] = btrefl.sel( channel = chan_name )

            # also set meta data
            a = {}
            a['units'] = attr.units[ichan]
            a['long_name'] = 'Synsat SEVIRI Brightness Temperature at %.1f um' % ( np.float(  chan_name[2:] ) / 10. )

            synsat[chan_name].attrs = a


        return synsat
