# Changelog

All notable changes to this project will be documented in this file.


## [Unreleased]

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
