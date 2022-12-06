---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# How to execute Snakemake commands from a directory

Sometimes, it can be useful to execute the Snakemake targets without Python coding from
the directory of a simulation. Calling directly Snakemake can be slightly difficult so
there is a Snek5000 command, `snek-make`, for this task. The help of this function can
be obtained with (the `!` is for calling a command in Jupyter):

```{code-cell} ipython3
!snek-make -h
```

From a simulation directory, `snek-make -l` lists the available targets. One can do for
example:

```sh
snek-make cleanall
snek-make compile
snek-make show_config
snek-make run_fg
```
