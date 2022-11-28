Roadmap
=======

Short term
----------

- Implement post processing API: with matplotlib and Paraview. Status:

  * Paraview_ reader is implemented. Requires clean up.
  * Pymech_ reader which extends xarray is implemented.

.. _paraview: https://github.com/snek5000/sandbox/blob/master/paraview/nekio.py
.. _pymech: https://pymech.readthedocs.io/en/latest/dataset.html

Long term
---------

- Interface Nek5000 states and time-integration event loop. More on this can be found
  at gh-issue-114_. Status:

  * Experiments are underway to interface using cffi_.
  * Fortran 2008 rewrite neko_ is now open-source. We should try linking to it.

.. _cffi: https://github.com/snek5000/sandbox/tree/master/interface/test_case
.. _neko: https://github.com/ExtremeFLOW/neko
.. _gh-issue-114: https://github.com/snek5000/snek5000/issues/114

Miscellaneous
-------------

.. todolist::
