import os, sys

import pandas as pd
import xarray as xr


RTTOV_PYTHON_WRAPPER = os.environ["RTTOV_PYTHON_WRAPPER"]

sys.path.append(RTTOV_PYTHON_WRAPPER)

import pyrttov


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
    print('no git hash can be obtained')

# Synsat Path
# ===========
__synsat_path__ = os.path.dirname(__file__)
