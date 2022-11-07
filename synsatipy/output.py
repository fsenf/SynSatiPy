#!/usr/bin/env python

import datetime
import starter

def prepare_global_attrs():

    attrs = {}
    attrs['author']      = "Fabian Senf"
    attrs['contact']     = "senf@tropos.de"
    attrs['institution'] = "Leibniz Institute for Tropospheric Research"
    attrs['creation_time'] = str( datetime.datetime.now() )
    attrs['synsat_version'] = starter.__version__
    attrs['synsat_githash'] = starter.__git_hash__
    attrs['license']  = 'CC-BY SA 3.0'
    attrs['_local_software_path'] = starter.__synsat_path__
    return attrs

