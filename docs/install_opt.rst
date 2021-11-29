Installing ParaView module
==========================

To install Paraview module:

- The most generic way is to use ``conda``::

   conda install -c conda-forge paraview

- In ArchLinux, the `ParaView package is built with system python`_, one can use::
   
   sudo pacman -S paraview; python -c 'import paraview'

.. _paraview package is built with system python: https://github.com/archlinux/svntogit-community/blob/packages/paraview/trunk/PKGBUILD

- The ParaView way of using ``pvpython`` tool is a bit complicated. And the most common hack is to append the virtual environment site-packages path to ``sys.path`` or ``$PYTHONPATH``. This would be the last resort.

