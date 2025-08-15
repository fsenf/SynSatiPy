import os, sys

import pandas as pd
import xarray as xr



try:
    if "RTTOV_PYTHON_WRAPPER" not in os.environ:
        raise EnvironmentError('Environment variable "RTTOV_PYTHON_WRAPPER" is not set.')

    RTTOV_PYTHON_WRAPPER = os.environ["RTTOV_PYTHON_WRAPPER"]
    print(f'RTTOV_PYTHON_WRAPPER environment variable found: {RTTOV_PYTHON_WRAPPER}')

    if not os.path.isdir(RTTOV_PYTHON_WRAPPER):
        raise NotADirectoryError(f'The path specified by RTTOV_PYTHON_WRAPPER does not exist: {RTTOV_PYTHON_WRAPPER}')

    sys.path.append(RTTOV_PYTHON_WRAPPER)
    print(f'Added {RTTOV_PYTHON_WRAPPER} to sys.path.')

    try:
        import pyrttov
        print('Successfully imported pyrttov module.')
    except ImportError as e:
        print(f'Failed to import pyrttov from {RTTOV_PYTHON_WRAPPER}: {e}')
        raise

except:

    # this dirty hack allows API reference documentation be generated without having RTTOV installed
    RTTOV_PYTHON_WRAPPER = 'Undefined'
    
    
    from abc import ABC
    class pyrttov_Empty():
        def __init__(self):
            self.Rttov = ABC

    pyrttov = pyrttov_Empty()

    print('FATAL ERROR: RTTOV is not found. Please set env variable "RTTOV_PYTHON_WRAPPER"!')

# Version
# =======
__version__ = 1.0.1


# Git Hash
# ========
try:
    import git
    repo = git.Repo(search_parent_directories=True)
    __git_hash__ = repo.head.object.hexsha
except:
    __git_hash__ = 'Undefined'
    print('no git hash can be obtained')

# Synsat Path
# ===========
__synsat_path__ = os.path.dirname(__file__)



# RTTOV Version
#==============
if '13.1' in RTTOV_PYTHON_WRAPPER:
    __rttov_version__ = 13.1

elif '13.2' in RTTOV_PYTHON_WRAPPER:
    __rttov_version__ = 13.2

else:
    __rttov_version__ = 'Unknown'


