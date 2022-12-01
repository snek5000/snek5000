.. _dev:

Developer Guide
===============

To install for development, execute::

   git clone https://github.com/snek5000/snek5000.git
   cd snek5000
   pip install -e ".[dev]"

.. note::

   Specifying ``[dev]`` would also install optional dependencies,
   namely:

   .. literalinclude:: ../../setup.cfg
      :start-at: [options.extras_require]
      :end-before: [options.packages.find]

.. toctree::
   :maxdepth: 1
   :caption: Reference

   solver
   output
   params
   phys_fields
   nek
   roadmap
   release

.. toctree::
   :maxdepth: 1
   :caption: How to for developers / maintainers of Snek5000 package

   edit_tutorials.md
