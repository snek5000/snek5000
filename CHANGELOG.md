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

(changelog/unreleased)=

## [Unreleased]

## [0.6.1b0] - 2021-05-18

### Changed

- {meth}`update_snakemake_config` and {func}`append_debug_flags` has a new
  parameter to optionally suppress compiler warnings during debug.
- Keyword arguments to pass optional template variables via `write_...` methods
  which render templates for `.box`, `SIZE` and `makefile_usr.inc` files.

### Fixed

- Remove `underflow` from debug flags

## [0.6.0b0] - 2021-04-16

### Added

- Tutorial and Snakemake workflows for packaging user code, see {ref}`packaging`
- Module {mod}`snek5000.util.smake` with helper utilities to set env, flags etc.

### Changed

- Much less boilerplate code for user code!
- Updated pre-commit hooks for development

### Deprecated

- Function {func}`snek5000.util.activate_paths`

### Removed

- Unused Snakemake rules from the top project level

### Fixed

- Support for 2D solvers and temp / scalar boundary conditions in Operators class.
- Attribute `sim.output.params` points to `params.output` as in FluidSim

## [0.5.0b0] - 2021-01-18

### Added

- Nek parameter `filter_modes` for HPFRT and `write_to_field_file`
- Function `load_simul` to load simulations from a directory.

### Changed

- Depend on `fluidsim-core` instead of `fluidsim`
- Parameters, entry points and magic implementation from fluidsim-core (#15)
- Output class now conforms to `fluidsim-core` API. File `params.xml` renamed
  to `params_simul.xml` (#16)

## [0.4.1b1] - 2020-10-26

### Changed
* Rewrite README and docs for better onboarding

## [0.4.1b0] - 2020-10-26

### Fixed
* Support for Python 3.6.x
* Support for FluidSim 0.3.3
* Descriptive error messages when class Output cannot resolve resources

## [0.4.0b1] - 2020-07-15

### Added
- Parameters for specifying mesh origin and ratio
- Coverage tests

### Changed
- Support for Nek5000 v19
- Cluster's default project

### Fixed
- Activate `$PATH` logic, added tests
- No error raised by `prepare_for_restart` after unlock
- Bug fixes while archiving: choosing paths of new tarball

## [0.3.1a0] - 2020-05-10

### Added
- More assets: templates, default snakemake config

### Fixed
- Source root path expands ~ and environment variables

## [0.3.0a0] - 2020-05-09

### Added

- Sub-package `assets` and module `output.base`
- Helper functions `source_root` and `get_asset`

### Changed

- Separate framework from the code and rename it to `snek5000`
- Documentation and readme to reflect the package

### Removed

- ABL source code

## [0.2.2] - 2020-05-08

### Added

- Pre-commit: black, flake8, isort fixing and linting support
- Jupyterlab and ipykernel configuration snakemake rules
- Job management script - organize.py
- New module: const

### Changed

- Parameters for Maronga case
- Compilation is now parallel
- Two-step archival, tar and compress

### Fixed

- Snakemake: gslib dependency before compiling
- Snakemake: Tee output to log file

### Removed

- Requirements files produced using pip-tools

## [0.2.1] - 2020-04-14

### Added
- Tar shell functions in activate script
- Module `snek5000.clusters` for job submission

### Changed
- Conda environment packages
- Reduced pressure residual tolerance for divergence check

### Fixed
- Bugfixes for simulation parameter loading, restart
- Snakefile dependencies for running a simulation

## [0.2.0] - 2020-03-22

### Added
- KTH toolbox
- Coriolis force
- Job submission in cluster
- More user_params

### Changed
- Archives use zstd compression
- user_params is a dictionary

### Fixed
- Initial condition bug in setting velocities in `useric`
- Cs - Cs**2 in `eddy_visc`
- Assert exit code of snakemake results in tests
- Subroutine `set_forcing` uses ux..  instead of vx

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
- New sub-packages and modules under `snek5000`: `solvers, output, info, log,
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
- Scripting for managing run parameters `snek5000.params`
- Python packaging
- Sphinx + Doxygen + Breathe documentation

[Unreleased]: https://github.com/exabl/snek5000/compare/0.6.0b0...HEAD
[0.6.1b0]: https://github.com/exabl/snek5000/compare/0.6.0b0...0.6.1b0
[0.6.0b0]: https://github.com/exabl/snek5000/compare/0.5.0b0...0.6.0b0
[0.5.0b0]: https://github.com/exabl/snek5000/compare/0.4.1b1...0.5.0b0
[0.4.1b1]: https://github.com/exabl/snek5000/compare/0.4.1b0...0.4.1b1
[0.4.1b0]: https://github.com/exabl/snek5000/compare/0.4.0b1...0.4.1b0
[0.4.0b1]: https://github.com/exabl/snek5000/compare/0.3.1a0...0.4.0b1
[0.3.1a0]: https://github.com/exabl/snek5000/compare/0.3.0a0...0.3.1a0
[0.3.0a0]: https://github.com/exabl/snek5000/compare/0.2.2...0.3.0a0
[0.2.2]: https://github.com/exabl/snek5000/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/exabl/snek5000/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/exabl/snek5000/compare/0.1.1...0.2.0
[0.1.1]: https://github.com/exabl/snek5000/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/exabl/snek5000/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/exabl/snek5000/releases/tag/0.0.1
