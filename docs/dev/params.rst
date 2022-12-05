Internal API of Parameters
==========================

.. seealso::

   :doc:`Tutorial on FluidDyn's ParamContainer API
   <fluiddyn:ipynb/tuto_paramscontainer>` and documentation of
   :class:`fluiddyn.util.paramcontainer.ParamContainer` which is
   extended for Snek5000.

   The function :func:`fluidsim_core.params.iter_complete_params` also comes in
   handy while building default Parameters.

Conversion
----------

.. autofunction:: snek5000.params._as_nek_value
.. autofunction:: snek5000.params._as_python_value
.. autofunction:: snek5000.params._get_params_nek

Inspection
----------

.. autofunction:: snek5000.params._check_path_like
.. autofunction:: snek5000.params._check_user_param_index


Input / Output
--------------

.. autofunction:: snek5000.params._complete_params_from_xml_file
.. autofunction:: snek5000.params._save_recorded_user_params
.. autofunction:: snek5000.params._load_recorded_user_params
.. autofunction:: snek5000.params._save_par_file
.. autofunction:: snek5000.params._str_par_file


Parameters class internals
--------------------------

.. autoclass:: snek5000.params.Parameters
   :private-members:
   :noindex:
