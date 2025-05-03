![](docs/images/btmovie.jpg)

# SynSatiPy


[![RTD](https://app.readthedocs.org/projects/synsatipy/badge/?version=latest)](https://app.readthedocs.org/projects/synsatipy/badge/?version=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15227962.svg)](https://doi.org/10.5281/zenodo.15227962)



- is a python package for atmospheric research (see [Science behind SynSatiPy](docs/Science-behind-SynSatiPy.md))

- allows to derive satellite images from weather forecasts or from climate simulations

SynSatiPy is a Python interface to the RTTOV software that helps to input model data (e.g. from IFS or from ICON) and loads emissivity catalogues and sensor specific files.

Currently, the SynSatiPy interface
- supports the following RTTOV versions: v13.1 and v13.2.
- provides interfaces to the following satellite sensors: SEVIRI
- is tested with python 3.10 or higher


## Getting Started

### Installation

Before SynSatiPy can be installed **RTTOV** must be downloaded, configured and installed on your target platform. See 
- https://nwp-saf.eumetsat.int/site/software/rttov/ or
- https://en.wikipedia.org/wiki/RTTOV_(radiative_transfer_code)




SynSatiPy can be installed via `pip`. It is recommended to install the SynSatiPy package into a separate python environment. Perhaps, the optimal way is to adjust this tutorial to your needs:
- [SynSatiPy Installation on DKRZ Levante](docs/Installation_on_Levante.md)

### Using SynSatiPy
SynSatiPy can be imported inside python scripts or jupyter notebooks. Examples are provided in the folder [Example Notebooks](docs/examples/) 

### User Guide
Further documentation is provided here: https://synsatipy.readthedocs.io.

## Contributing
Please feel invited to contributed to the SynSatiPy python package (via pull requests). Possible extension are (not exclusive):
- implementation of further satellite sensor interfaces
- implementation of further model input interfaces

Please provide bug reports or ideas for extensions as issues!


