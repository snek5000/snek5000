# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

Type of changes
---------------

Added for new features.
Changed for changes in existing functionality.
Deprecated for soon-to-be removed features.
Removed for now removed features.
Fixed for any bug fixes.
Security in case of vulnerabilities.

-->

## [Unreleased]
- Paraview I/O for loading and plotting functions

## [0.1.1] - 2020-01-27

### Added
- Templates in `abl.templates` subpackage
- Expand parameters and write methods in class `Operators`
- Improved tests and documentation
- Solver `abl` respects parameters and writes box and SIZE files.

### Changed
- Snakecase for `nek` parameters

## [0.1.0] - 2020-01-23

### Added
- Uses `fluidsim` framework for creating a scripting layer
- Package `abl` with a single module and an `abl.Output` class
- New sub-packages and modules under `eturb`: `solvers, output, info, log,
  make, magic, operators`
- Testing with `pytest`, and CI on GitHub actions
- Detailed documentation
- Versioning with `setuptools_scm`

### Changed
- Extra requirements `[test]` renamed to `[tests]`
- Rename case files `3D_ABL` -> `abl` and directory `abl_nek5000` -> `abl`
- Overall reorganization of modules and Snakemake + configuration files.

## [0.0.1] - 2020-01-17

### Added
- Scripting for managing run parameters `eturb.params`
- Python packaging
- Sphinx + Doxygen + Breathe documentation
