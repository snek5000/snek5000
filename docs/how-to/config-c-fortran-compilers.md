# How to configure C and Fortran compilers

As pointed out in the tutorial on {ref}`configuring` Snek5000, it relies on a
default configuration file with sane defaults for C and Fortran compilers such
as `gcc`, `gfortran` and its MPI wrappers and flags.

You can also generate a machine / user specific configuration file using
`snek-generate-config` command-line tool which would copy the default
configuration to `$HOME/.config/snek5000.yml` and modify it to your needs.
{ref}`Read more about this here <config_files>`.

Other possibilities include overriding from the {ref}`Python simulation script <override_config>` and via {ref}`environment variables <override_config_env>`.
