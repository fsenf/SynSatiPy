# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] 2026-08-03

### Added

#### Aerosol Support
- New `aerosoltools` module for CAMS/OPAC aerosol species mapping and number-to-mass conversion
- `use_aerosols` parameter for DataHandler and SynSat workflows with configurable species
- HAMlite aerosol processing pipeline with automatic file detection and integration
- Support for aerosol file handling in RTTOV via `FileScaer` coefficient files

#### MODIS/EOS Instrument Support
- New `load_eos_modis()` method supporting EOS-1 (Terra) and EOS-2 (Aqua) satellites
- All 36 MODIS bands (0.4–14.4 μm) with default channel selection (thermal/water vapor bands 20, 22, 27–29, 31–33)
- Polar-orbiting geometry handling with dynamic subsatellite longitude support
- MODIS coefficient file integration for both Terra and Aqua variants

#### Data Handler
- HAMlite flavor detection and processing pipeline
- Support for external geofile input via `geofile` parameter
- New `hamlite01` example dataset

### Changed

#### Core Processing
- Modified gas stacking in `data2profile()` to accommodate aerosols (list-based instead of `np.stack()`)
- Enhanced GasId mapping to include aerosol RTTOV IDs (81–89 for CAMS species)
- Added pressure level ordering detection (top-to-bottom vs bottom-to-top) for correct surface variable assignment
- Improved subsatellite longitude handling with optional nadir-only viewing geometry support

#### Instrument Configuration
- Extended `load_instrument()` to support "modis" alongside "seviri", "abi", and "fci"
- HAMlite file naming refactored with explicit `hamlite-aerosols` flavor variant

#### Tests & Examples
- Parametrized test cases for MODIS satellite variants
- Centralized example data paths under `/work/bb1376/data/synsatipy/example-data/`
- Updated test infrastructure to support geofile return options

### Fixed

- Proper handling of `lon0=None` for nadir-only viewing geometry (sets azimuth/zenith to zero)
- Correct surface humidity extraction based on pressure level ordering
- Code formatting and style consistency throughout

## [1.1.0] - 2025-11-14

### Added
- MTG-FCI instrument support with 16 spectral channels (0.444-13.30 μm)
- `load_mtg_fci()` method for FCI configuration
- Enhanced HAMlite data processing with improved file merging
- Hurricane-centric data processing support (flavor=ifces2)
- Comprehensive FCI test coverage

### Changed
- Extended supported instruments to include "fci" alongside "seviri" and "abi"
- Improved ICON data input processing with better pattern matching
- Enhanced test cleanup for notebook output files

### Fixed
- Critical bugfix: Proper handling of data together with masks in DataHandler
- FCI channel specifications and wavelength assignments
- HAMlite file merging operations
- Removed dead code and unreachable conditional branches


## [1.0.1b] - 2025-08-15

### Added

#### Instrument Support
- Support for GOES-ABI instrument alongside MSG-SEVIRI
- New `load_goes_abi()` method for GOES-ABI configuration with 16 spectral channels
- Generic `load_instrument()` method for instrument-agnostic loading

#### Code Structure and Organization
- Parametrized tests for both SEVIRI and ABI instruments using pytest
- Test utilities for loading predefined atmospheric profiles
- Comprehensive test coverage for different channel configurations
- Bash script for running both unit tests and Jupyter notebook execution

#### Data Handling
- Enhanced error handling with specific exception types (e.g., `KeyError`, `FileNotFoundError`)
- Improved filename pattern matching and sorting for data processing
- Support for symbolic link creation for data management

#### Documentation
- NumPy-style docstrings throughout the codebase
- Enhanced API documentation structure
- Improved function parameter documentation

### Changed

#### Instrument Configuration
- Refactored instrument loading with case-insensitive instrument selection
- Renamed variables from `chan_list_seviri`/`nchan_seviri` to generic `chan_list_instrument`/`nchan_instrument`
- Renamed `load_seviri()` to `load_msg_seviri()` for consistency
- Updated instrument attribute naming for better clarity

#### Code Quality
- Replaced bare `except` clauses with specific exception handling
- Improved code modularity and separation of concerns
- Enhanced variable naming conventions for better readability

#### Testing Infrastructure
- Improved test script with sorted output and hidden path exclusion
- Enhanced workflow testing for multiple instruments
- Better test organization and parameterization

### Fixed

#### File Processing
- File path handling in test scripts and data processing
- Channel list sorting in workflow execution
- Hidden file/directory exclusion in file search operations

#### Data Processing
- Pressure calculation and coordinate handling in ERA data processing
- Specific humidity clipping with configurable minimum values
- Time coordinate selection and merging in multi-dimensional datasets

### Technical Details

#### Dependencies
- Maintains compatibility with existing pyrttov, xarray, and numpy dependencies
- Added support for pytest parameterization features
- Enhanced Jupyter notebook execution capabilities

#### Performance
- Optimized file searching with improved find commands
- Better memory management in chunked data processing
- Streamlined instrument loading procedures

## [1.0.0] - 2024-04-16

### Added
- Initial release of SynSatiPy
- MSG-SEVIRI instrument support for satellite radiance simulation
- ERA5 and ICON model data input support
- RTTOV integration for radiative transfer calculations
- Basic test framework and example notebooks
- Documentation structure and API reference

### Dependencies
- pyrttov for radiative transfer calculations
- xarray for multi-dimensional data handling
- numpy for numerical operations
- netCDF4 for data I/O
