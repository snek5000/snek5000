.. snek5000 documentation master file, created by
   sphinx-quickstart on Wed Dec 25 01:55:26 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to *snek5000*'s documentation!
===========================================

Snek5000 is a Python package and a thin interface over Nek5000_. It provides a
framework to organize parameters and launch multiple simulations. Snek5000's
internals rely on FluidSim's core_ to build its API.

.. raw:: html


   <!--
      Icon derived from "wind slap icon" by Lorc. Available at
      https://game-icons.net/1x1/lorc/wind-slap.html .
      License: https://creativecommons.org/licenses/by/3.0/
   -->
   <img style="float: right;" src="_static/icon.svg" width="100rem"/>

+------------+-----------------------------------+
| Repository | https://github.com/exabl/snek5000 |
+------------+-----------------------------------+
| Version    | |release|                         |
+------------+-----------------------------------+

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   README
   tutorials

User Guide
----------

.. autosummary::
   :toctree: _generated/
   :caption: User Guide

   snek5000

.. toctree::
   :maxdepth: 1
   :caption: Help & Reference

   roadmap
   nek5000
   internals
   filtering
   release
   CONTRIBUTING
   CHANGELOG
   AUTHORS
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _core: https://fluidsim.readthedocs.io/en/latest/generated/fluidsim_core.html
.. _Nek5000: https://nek5000.github.io/NekDoc/
