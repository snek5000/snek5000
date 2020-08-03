Roadmap
=======

Short term
----------

- Implement post processing API: with matplotlib and Paraview. Status:
  * Paraview_ reader is implemented. Requires clean up.
  * Pymech_ reader which extends xarray is implemented.

.. _paraview: https://github.com/exabl/sandbox/blob/master/paraview/nekio.py
.. _pymech: https://pymech.readthedocs.io/en/latest/dataset.html

Long term
---------

- Interface Nek5000 states and time-integration event loop. Status:
  * Experiments are underway to interface using cffi_.

.. _cffi: https://github.com/exabl/sandbox/tree/master/interface/test_case

Miscellaneous
-------------

.. todolist::

