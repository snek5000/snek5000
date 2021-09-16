.. _configuring:

Configuring compilation and execution
=====================================

Since ``snek5000`` acts as a thin interface automation of not just setting up a
run, but also the **compilation** and **execution**, you would often need to customize
the compiler and its flags. By default it is configured to use the gcc,
gfortran and OpenMPI to compile the code.


.. literalinclude:: ../src/snek5000/assets/default_configfile.yml
   :language: yaml

Customization
-------------

You are expected to keep one configuration file for per machine / cluster where
``snek5000`` is executed. When a file is not found during runtime it issues a
warning similar to::

   WARNING  Missing a configuration file describing compilers and flags. Create one at either of the following paths to avoid future warnings:
            /home/avmo/.config/snek5000/<hostname>.yml
            /home/avmo/src/snek5000/snek5000-canonical/src/snek5000_canonical/etc/<hostname>.yml
   INFO     Using default configuration for now:
            /home/avmo/src/snek5000/snek5000/src/snek5000/assets/default_configfile.yml

As the warnings suggest, there are two possible paths where you can save your configuration:

1. ``~/.config/snek5000/<hostname>.yml``
2. ``<path to package root>/etc/<hostname>.yml``

.. note::

   ``<hostname>`` is usually the output of the ``hostname`` command in POSIX,
   or alternatively::

      python -c 'import socket; print(socket.gethostname())'

   See :meth:`snek5000.output.base.Output.get_configfile` for more details.

Overriding configuration with environment variable
--------------------------------------------------

To allow for reproducible runs, it is discouraged to rely on environment
variables to set the configuration. Nevertheless, it is possible to do so by
using the following function call in the user ``Snakefile``.

.. code-block:: python

   Output.update_snakemake_config(config, CASE, env_sensitive=True)

See :meth:`snek5000.output.base.Output.update_snakemake_config` and :ref:`user_snakefile` for more details
