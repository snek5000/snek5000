# How to rebuild Nek5000 libraries and tools

For a fresh git clone of Nek5000 sources, Snek5000 takes care of the build
automatically. However if your C and Fortran compiler with its related
toolchain gets an update, or if you change it intentionally you may need to
recompile Nek5000 libraries again. To do so:

```sh
cd $NEK_SOURCE_ROOT
git clean -xdf
```

Next time you execute a Snek5000 solver, the libraries would be rebuild.
