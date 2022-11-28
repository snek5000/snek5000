Installation
#############

You should always have these environment variables set, pointing to the Nek5000
source code and the ``bin`` directory within

.. code-block:: bash

   export NEK_SOURCE_ROOT="/path/to/Nek5000"
   export PATH="$PATH:$NEK_SOURCE_ROOT/bin"

.. important::

   **Nek5000 dependencies**: Ensure you have the necessary compilers, build
   tools and libraries as recommended in the :doc:`Nek5000 documentation
   <nek:quickstart>`.

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
interpreter of your choice, download the `environment.yaml file`_ to your hard disk and
then execute:

.. tab:: PyPy

   ::

      conda create --name env-snek -c conda-forge pypy pip pandas xarray
      conda activate env-snek
      conda install --yes --file environment.yaml
      pypy -m pip install snek5000

.. tab:: CPython

   ::

      conda create --name env-snek -c conda-forge python pip
      conda activate env-snek
      conda install --yes --file environment.yaml
      python -m pip install snek5000

.. _PyPy: https://www.pypy.org/
.. _conda: https://docs.conda.io/projects/conda/en/latest/user-guide/index.html
.. _mamba: https://mamba.readthedocs.io/en/latest/installation.html
.. _environment.yaml file: https://github.com/snek5000/snek5000/raw/main/requirements/environment.yaml

.. toctree::
   :caption: Optional dependencies

   install_opt.rst
