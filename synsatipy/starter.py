import os, sys

import pandas as pd
import xarray as xr



try:
    RTTOV_PYTHON_WRAPPER = os.environ["RTTOV_PYTHON_WRAPPER"]

    sys.path.append(RTTOV_PYTHON_WRAPPER)

    import pyrttov

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
__version__ = 0.1


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


