# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

<!-- (changelog/unreleased)= -->

## [Unreleased]

## [0.9.2] - 2023-08-23

### Added
- Donation links.

### Fixed

- {func}`snek5000.find_configfile` removes call to deprecated function.
- Explicit `ValueError` when no coordinates are defined and history points
  object's `load` method is invoked.
- Minor corrections in `README.md` and documentation and JOSS manuscript.

## [0.9.1] - 2023-05-01

### Added

- New command `snek-make-nek` to clean and rebuild Nek5000 tools
- JOSS paper draft

Documentation

- How to use adaptive time step
- How to configure C and Fortran compilers
- Document the new copier template

### Changed

- Use `remaining_clock_time` by default
- Replace isort and flake8 with ruff, upgrade hooks

## [0.9.0] - 2023-01-11

### Added

- {mod}`snek5000.output.remaining_clock_time`.
- {func}`snek5000.output.base.Output.post_init_create_additional_source_files`,
  {func}`snek5000.resources.get_base_templates` and
  {func}`snek5000.resources.get_base_template`.
- {class}`snek5000.output.spatial_means.SpatialMeans`.
- New block `user_size` in `SIZE.j2` template (see {mod}`snek5000.resources`).

### Removed

- Functions deprecated in 0.8.0 (`source_root`, `get_asset`, `get_root`,
  `get_configfile`, `_complete_params_from_par_file`).
- Subpackage `snek5000.assets`.

## [0.8.0] - 2022-12-06

This is the first stable version and is the result of a huge work (more than 550 commits
and [60 closed issues](https://github.com/snek5000/snek5000/milestone/1)). To summarize,
we work a lot on stability, on improving the API, the logging and the user experience,
and on improving our [documentation](https://snek5000.readthedocs.io) and
[tutorials](https://snek5000.readthedocs.io/en/latest/tutorials.html). The following
lists are a very incomplete lists of the additions, changes and deprecations.

### Added

- Commands
  [`snek-make`](https://snek5000.readthedocs.io/en/latest/how-to/snek-make.html),
  [`snek-restart`](https://snek5000.readthedocs.io/en/latest/how-to/restart.html),
  `snek-info`, `snek-ipy-load` and `snek-generate-config`.
- Functions {func}`snek5000.util.restart.load_for_restart`,
  {func}`snek5000.params.load_params`
- {mod}`snek5000.util.files`
- {meth}`snek5000.output.base.Output.get_field_file` to locate a field file
- Mandatory key `MPIEXEC_FLAGS` in Snakemake config
- {class}`snek5000.output.history_points.HistoryPoints` for
  {ref}`Nek5000 history points <nek:features_his>`
- {class}`snek5000.output.phys_fields.PhysFields` now fully functional with `load` and
  `get_var` methods provided by classes under {mod}`snek5000.output.readers`.
- Support for number of processes detection in OAR clusters
- {meth}`snek5000.output.base.Output._set_info_solver_classes` to customize Output child
  classes
- Environment variable `SNEK_UPDATE_CONFIG_ENV_SENSITIVE`,
  {meth}`snek5000.output.base.Output.write_snakemake_config` to help the user easily
  modify environment variables during Snakemake rule execution. See
  {ref}`override_config`.

### Changed

- Mandatory environment variable `NEK_SOURCE_ROOT`.
- `params.oper.elem.staggered` has a new default value `auto`, which sets staggered grid
  if a linear solver is used and a collocated one if some other solver is used.
  Explicitly setting `params.oper.elem.staggered = True` is required to maintain
  previous default behaviour.
- {func}`snek5000.util.files.next_path` gets `force_suffix` and `return_suffix`
  parameters
- {meth}`snek5000.output.base.Output._save_info_solver_params_xml` updates `.par` and
  `params_simul.xml` file on loading for restart
- Shorter output while executing `genmap`
- Field files will be stored in sessions enabling restart with symlinking of restart
  files and avoids clobbering existing solution files
- Support extension `.usr.f` to facilitate syntax highlighting and which would be copied
  as a `.usr` file upon {meth}`snek5000.output.base.Output.copy`
- The use of `params.nek.general.user_params` are replaced by a more powerful
  {meth}`snek5000.params.Parameters._record_nek_user_params` method.

### Deprecated

- {func}`snek5000.params._complete_params_from_par_file` (renamed as
  {func}`snek5000.params.complete_params_from_par_file`).
- {func}`snek5000.util.restart.prepare_for_restart`
- Passing rules as iterables to {meth}`snek5000.make.Make.exec`. Pass positional
  parameters instead.
- {func}`snek5000.source_root` (renamed as {func}`snek5000.get_nek_source_root`).
- {meth}`snek5000.output.base.Output.get_root` (renamed as
  {meth}`snek5000.output.base.Output.get_path_solver_package`).
- {meth}`snek5000.output.base.Output.get_configfile` (use a string `"config_simul.yml"`
  instead in user Snakefile).
- The `warnings` parameter in
  {meth}`snek5000.output.base.Output.update_snakemake_config` is deprecated! Use
  `verbosity=0` (now default) to disable warnings.

### Removed

- Parameter `warnings` in {func}`snek5000.util.smake.append_debug_flags` is replaced by
  a separate function {func}`snek5000.util.smake.set_compiler_verbosity`.

### Fixed

- Detection of linear Nek5000 solvers
- Append debug flags to config, even if CFLAGS and FFLAGS are missing

## [0.7.0b0] - 2021-09-16

### Added

- Ability to customize number of processes with {meth}`snek5000.make.Make.exec`
- Documentation on configuring `snek5000` compilation and execution

### Changed

- Use rich for logging
- No need to wait for `<case>.f` file which is deleted by new Nek5000 version
- {func}`snek5000.load` alias for {func}`snek5000.load_simul` which also loads from
  current directory when no argument is passed
- Fix {meth}`snek5000.solvers.base.InfoSolver._complete_params_with_default` into a
  classmethod (thanks [@paugier])
- `params.oper.max.order_time` is now a property
  {any}`snek5000.operators.Operators.max_order_time`

### Removed

- Rule `srun` renamed as called `run_fg`

### Fixed

- Allow `name_solver` to be different from the "package name" (thanks [@paugier])

## [0.6.1b0] - 2021-05-18

### Changed

- {meth}`update_snakemake_config` and {func}`append_debug_flags` has a new parameter to
  optionally suppress compiler warnings during debug.
- Keyword arguments to pass optional template variables via `write_...` methods which
  render templates for `.box`, `SIZE` and `makefile_usr.inc` files.

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
- Output class now conforms to `fluidsim-core` API. File `params.xml` renamed to
  `params_simul.xml` (#16)

## [0.4.1b1] - 2020-10-26

### Changed

- Rewrite README and docs for better onboarding

## [0.4.1b0] - 2020-10-26

### Fixed

- Support for Python 3.6.x
- Support for FluidSim 0.3.3
- Descriptive error messages when class Output cannot resolve resources

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
- Job management script - `organize.py`
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
- Cs - Cs\*\*2 in `eddy_visc`
- Assert exit code of snakemake results in tests
- Subroutine `set_forcing` uses ux.. instead of vx

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
- New sub-packages and modules under `snek5000`:
  `solvers, output, info, log, make, magic, operators`
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

[0.0.1]: https://github.com/snek5000/snek5000/releases/tag/0.0.1
[0.1.0]: https://github.com/snek5000/snek5000/compare/0.0.1...0.1.0
[0.1.1]: https://github.com/snek5000/snek5000/compare/0.1.0...0.1.1
[0.2.0]: https://github.com/snek5000/snek5000/compare/0.1.1...0.2.0
[0.2.1]: https://github.com/snek5000/snek5000/compare/0.2.0...0.2.1
[0.2.2]: https://github.com/snek5000/snek5000/compare/0.2.1...0.2.2
[0.3.0a0]: https://github.com/snek5000/snek5000/compare/0.2.2...0.3.0a0
[0.3.1a0]: https://github.com/snek5000/snek5000/compare/0.3.0a0...0.3.1a0
[0.4.0b1]: https://github.com/snek5000/snek5000/compare/0.3.1a0...0.4.0b1
[0.4.1b0]: https://github.com/snek5000/snek5000/compare/0.4.0b1...0.4.1b0
[0.4.1b1]: https://github.com/snek5000/snek5000/compare/0.4.1b0...0.4.1b1
[0.5.0b0]: https://github.com/snek5000/snek5000/compare/0.4.1b1...0.5.0b0
[0.6.0b0]: https://github.com/snek5000/snek5000/compare/0.5.0b0...0.6.0b0
[0.6.1b0]: https://github.com/snek5000/snek5000/compare/0.6.0b0...0.6.1b0
[0.7.0b0]: https://github.com/snek5000/snek5000/compare/0.6.1b0...0.7.0b0
[0.8.0]: https://github.com/snek5000/snek5000/compare/0.7.0b0...0.8.0
[0.9.0]: https://github.com/snek5000/snek5000/compare/0.8.0...0.9.0
[0.9.1]: https://github.com/snek5000/snek5000/compare/0.9.0...0.9.1
[0.9.2]:  https://github.com/snek5000/snek5000/compare/0.9.1...0.9.2
[@paugier]: https://github.com/paugier
[unreleased]: https://github.com/snek5000/snek5000/compare/0.9.2...HEAD
