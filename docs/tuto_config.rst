.. _configuring:

Configuring compilation and execution
=====================================

Since ``snek5000`` acts as a thin interface automation of not just setting up a
run, but also the **compilation** and **execution**, you would often need to customize
the compiler and its flags. By default it is configured to use gcc,
gfortran and OpenMPI to compile the code.

.. literalinclude:: ../src/snek5000/resources/default_configfile.yml
   :language: yaml

.. _config_files:

Customization via config files
------------------------------

You are expected to keep one configuration file for per machine / cluster where
``snek5000`` is executed. When a file is not found during runtime it issues a
warning similar to::

   WARNING: Missing a configuration file describing compilers and flags. Create one at either of the following paths to avoid future warnings:
   /home/docs/.config/snek5000/<hostname>.yml
   /home/docs/.config/snek5000.yml
   /home/docs/src/snek5000/snek5000-canonical/src/snek5000_canonical/etc/<hostname>.yml
   The command `snek-generate-config` could be used to create a user config file for you.
   Using default configuration for now:
   /home/docs/src/snek5000/snek5000/src/snek5000/resources/default_configfile.yml

As the warnings suggest, (i) a simple method to avoid these warnings is to
run the command ``snek-generate-config`` and (ii) there are three possible
paths where you can save your configuration:

1. ``~/.config/snek5000/<hostname>.yml``
2. ``~/.config/snek5000.yml``
3. ``<path to package root>/etc/<hostname>.yml``

.. note::

   ``<hostname>`` is usually the output of the ``hostname`` command in POSIX,
   or alternatively::

      python -c 'import socket; print(socket.gethostname())'

   See :meth:`snek5000.output.base.Output.find_configfile` for more details.

.. _override_config:

Overriding configuration in the launching script
------------------------------------------------

One can override a configuration variable from a launching script by calling
the function :meth:`snek5000.output.base.Output.write_snakemake_config`:

.. code-block:: python

   sim.output.write_snakemake_config(
       custom_env_vars={"MPIEXEC_FLAGS": "--report-pid PID.txt"}
   )

.. _override_config_env:

Overriding configuration with environment variables
---------------------------------------------------

To allow for reproducible runs, it is discouraged to rely on environment
variables to set the configuration. Nevertheless, it is possible to do so by
setting up the environment variable ``SNEK_UPDATE_CONFIG_ENV_SENSITIVE`` as
follows::

   export SNEK_UPDATE_CONFIG_ENV_SENSITIVE=1
   export MPIEXEC_FLAGS="--report-pid PID.txt"

It is also possible to force this behavior in the user ``Snakefile`` by using
the following function call.

.. code-block:: python

   Output.update_snakemake_config(config, CASE, env_sensitive=True)

See :meth:`snek5000.output.base.Output.update_snakemake_config` and :ref:`user_snakefile` for more details


On compiling and running simultaneous simulations
-------------------------------------------------

Snek5000 supports compiling multiple simulation runs from different terminals
or cluster jobs in realtime. It will also take care of rebuilding the Nek5000
libraries if the compiler configuration changes. We use the ``filelock``
library to avoid multiple rebuilds. See :ref:`nek5000make` for more
information.

.. warning::

    There is a small caveat with this solution. If a series of jobs are
    launched which uses various compiler configurations, then it would
    rebuild Nek5000 tools and libraries again and again during
    ``sim.output.post_init`` - and suddenly some library would be missing
    during the ``sim.make.exec`` call. As long as all subsequent jobs use
    the same compiler configuration, it should work.
