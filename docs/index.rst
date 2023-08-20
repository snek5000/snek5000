.. snek5000 documentation main file, created by
   sphinx-quickstart on Wed Dec 25 01:55:26 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to *Snek5000*'s documentation!
======================================

Snek5000 is a Python package and a thin interface over Nek5000_. It provides a
framework to (i) organize parameters, (ii) launch/restart multiple simulations
and (iii) load simulations to read the associated parameters/data and produce
nice figures/movies.

.. raw:: html

   <!--
      Icon derived from "wind slap icon" by Lorc. Available at
      https://game-icons.net/1x1/lorc/wind-slap.html .
      License: https://creativecommons.org/licenses/by/3.0/
   -->

+------------+--------------------------------------+
| Repository | https://github.com/snek5000/snek5000 |
+------------+--------------------------------------+
| Version    | |release|                            |
+------------+--------------------------------------+

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   intro
   install
   tutorials.md
   how-to/index.md

.. toctree::
   :maxdepth: 1
   :caption: User guide & Python API

   autosum

.. toctree::
   :maxdepth: 1
   :caption: Help & Reference

   dev/index.rst
   CONTRIBUTING
   CHANGELOG
   authors.md
   license
   Source code on GitHub <https://github.com/snek5000/snek5000>

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _core: https://fluidsim.readthedocs.io/en/latest/generated/fluidsim_core.html
.. _Nek5000: https://nek5000.github.io/NekDoc/
