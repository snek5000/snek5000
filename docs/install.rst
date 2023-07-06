Installation
#############

Preliminary: setup Nek5000
==========================

You should always have the environment variable ``NEK_SOURCE_ROOT`` pointing to
the Nek5000 source code directory:

.. code-block:: bash

   export NEK_SOURCE_ROOT="/path/to/Nek5000"

.. note::

   You may want to also add the Nek5000 ``bin`` directory in your path (with
   something like ``export PATH=$PATH:$NEK_SOURCE_ROOT/bin``) to also be able
   to use Nek5000 directly without Snek5000, but it should not be mandatory for
   Snek5000.

.. important::

   **Nek5000 version**: To ensure compatibility, you should use our fork
   `snek5000/Nek5000`_. It contains some
   bug fixes and enhancements on top of Nek5000 v19 [#fork]_. We cannot use
   the bleeding-edge ``master`` branch of Nek5000 due to another bug [#master]_.

   **Nek5000 dependencies**: Ensure you have the necessary compilers, build
   tools and libraries as recommended in the :doc:`Nek5000 documentation
   <nek:quickstart>`.

.. _snek5000/Nek5000: https://github.com/snek5000/Nek5000

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


Footnotes
=========

.. [#fork] The following commits in the `snek5000/Nek5000`_ fork compared to
   Nek5000 v19 release are essential for Snek5000 to work correctly.

   1. Fixes bug which can cause simultaneously launched simulation to fail: `Nek5000/Nek5000@3e53855 <https://github.com/Nek5000/Nek5000/commit/3e538555256b047a6d534111efa669e0557d0979>`_
   2. Allows for upto 20 userparams `Nek5000/Nek5000@5581603 <https://github.com/Nek5000/Nek5000/commit/5581603ce76cbf54d9b8a5e73b6044a7ba8678dd>`_

   These are also available in the upstream ``master`` branch, but has not been
   released yet. If you have your own Nek5000 fork, consider executing ``git
   cherry-pick`` of these commits.

.. [#master] The ``master`` branch handles the working directory differently as
   compared to Nek5000 v19. We will try to support this when they release the
   new version and finalize it. See `issue #270
   <https://github.com/snek5000/snek5000/issues/270>`_ for more details.
