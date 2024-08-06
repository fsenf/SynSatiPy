#!/usr/bin/env python

"""Output module for SynSat data."""

import datetime

import synsatipy.starter as starter


def prepare_global_attrs():
    """
    Prepare the global attributes.
    
    Returns
    -------
    attrs : dict
        The global attributes.

    Notes
    -----
    The global attributes are:
    - author : str
        The author of the data.
    - contact : str
        The contact email of the author. 
    - institution : str
        The institution of the author.
    - creation_time : str
        The creation time of the data.
    - synsat_version : str
        The SynSat version.
    - synsat_githash : str
        The SynSat git hash.
    - license : str
        The license of the data.
    - _local_software_path : str
        The local software path.
    """
    attrs = {}
    attrs["author"] = "Fabian Senf"
    attrs["contact"] = "senf@tropos.de"
    attrs["institution"] = "Leibniz Institute for Tropospheric Research"
    attrs["creation_time"] = str(datetime.datetime.now())
    attrs["synsat_version"] = starter.__version__
    attrs["synsat_githash"] = starter.__git_hash__
    attrs["license"] = "CC-BY SA 3.0"
    attrs["_local_software_path"] = starter.__synsat_path__
    return attrs
