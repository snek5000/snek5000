Installing ParaView package
===========================
.. note::
   Using ParaView as a reader is a work in progress!

To install ParaView package:

- The most generic way is to use ``conda``::

   conda install -c conda-forge paraview

- In ArchLinux, the `ParaView package is built with system python`_, one can use::
   
   sudo pacman -S paraview; python -c 'import paraview'

.. _paraview package is built with system python: https://github.com/archlinux/svntogit-community/blob/packages/paraview/trunk/PKGBUILD

- In many ParaView distributions, the package is not packaged along with the system ``python``. Instead it comes with a
  separate ``pvpython`` executable. Installing ``snek5000`` into ``pvpython`` or to use ``snek5000`` in the "Python Shell" 
  in ParaView GUI is a bit complicated. One possible hack is to create a virtual environment using the same Python 
  version as in ``pvpython`` and append the virtual environment's site-packages path to ``sys.path`` or environment 
  variable ``$PYTHONPATH``.







