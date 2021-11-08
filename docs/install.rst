Installation
#############

You should always have these environment variables set, pointing to the Nek5000
source code and the ``bin`` directory within

.. code-block:: bash

   export NEK_SOURCE_ROOT="/path/to/Nek5000"
   export PATH="$PATH:$NEK_SOURCE_ROOT/bin"

Install using pip
=================

Snek5000 requires Python version |py_min_version| and above. For most purposes,
we recommend creating a `virtual environment`_ and then running::

   pip install snek5000

.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments


See :ref:`dev` if you wish to install for development.

Install using conda / mamba
===========================

In certain cases, typically:

- in an OS where at least Python version |py_min_version| is unavailable, or
- to use PyPy_ instead of CPython,

a simple ``pip install snek5000`` may not cut it.  Then, it is recommended to use conda_ (or
mamba_) to set up the Python environment first. To install Snek5000 with a Python
interpreter of your choice:

.. tab:: PyPy

   ::

      conda create -n my-env -c conda-forge pypy pip pandas xarray
      conda activate my-env
      pypy -m pip install snek5000

.. tab:: CPython

   ::

      conda create -n my-env -c conda-forge python pip
      conda activate my-env
      python -m pip install snek5000

.. _PyPy: https://www.pypy.org/
.. _conda: https://docs.conda.io/projects/conda/en/latest/user-guide/index.html
.. _mamba: https://mamba.readthedocs.io/en/latest/installation.html
