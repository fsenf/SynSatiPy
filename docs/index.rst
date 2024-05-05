.. CTyPyTool documentation master file, created by
   sphinx-quickstart on Wed Dec 22 10:52:50 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/Rempel_Fig1.jpg
    :alt: Deep Convection over Germany


SynSatiPy: An Interface to RTTOV for the Computation of Synthetic Satellite Imagery
===================================================================================


- is a python package for atmospheric research

- allows to derive satellite images from weather forecasts or from climate simulation

SynSatiPy is a Python interface to the RTTOV software that help to input model data (e.g. from IFS or from ICON) and loads emissivity catalogues and sensor specific files.


.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   Installation_on_Levante.md


.. toctree::
   :maxdepth: 1
   :caption: Examples

   Science-behind-SynSatiPy.md

   examples/01-First-Steps-with-SynSatiPy.ipynb
   examples/02-Run-Synsat-for-ERA5-Data.ipynb
   examples/03-Compare-ERA5-Synsat-to-Meteosat.ipynb
   examples/04-Run-Synsat-for-ICON-Data.ipynb
   examples/05-Compare-ICON-Synsat-to-Meteosat.ipynb


.. toctree::
   :caption: API Reference
   :maxdepth: 3

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
