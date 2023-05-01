# How to rebuild Nek5000 libraries and tools

For a fresh git clone of Nek5000 sources, Snek5000 takes care of the build
automatically. However if your C and Fortran compiler with its related toolchain gets an
update, or if you change it intentionally you may need to recompile Nek5000 libraries
again. To do so:

```sh
snek-make-nek --clean-git
```
