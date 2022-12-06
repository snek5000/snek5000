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

# How to restart simulations

Restarting simulations with Nek5000 can be tricky. For example, it is easy to erase some
results from the initial simulation! To fix this issue Snek5000 uses the notion of
"sessions", meaning that some results of the different simulations are saved in
directories `session_00`, `session_01`, ...

Moreover, there are with Nek5000 two different methods to restart a simulation:

1. (builtin with Nek5000) from a state file (but the time-stepping scheme has to be
   initialize so the restart is not perfect),
1. (with the [KTH toolbox]) from restart files (only works with solvers using this
   toolbox).

With Snek5000, restarting can be done with the command line `snek-restart` (recommanded)
or with a Python function {func}`snek5000.load_for_restart`. In this page, with focus on
the former method.

One can get the documentation of the command with

```{code-cell} ipython3
!snek-restart -h
```

Let's give few examples. We start from a simulation using the `snek5000-phill` solver
(which uses the [KTH toolbox]).

1. To restart the simulation in a new session (no compilation needed) from the last
   state file, one can run:

   ```sh
   snek-restart /path/of/the/simulation --use-start-from -1 --end-time 0.005
   ```

   ```{note}
   This method is used in [the tutorial using our snek5000-tgv solver](../tuto_tgv.myst.md#restart-to-run-further).
   ```

1. To restart the simulation in a new session (no compilation needed) from the
   [KTH toolbox] restart files:

   ```sh
   snek-restart /path/of/the/simulation --use-checkpoint 1 --end-time 0.005
   ```

1. Alternatively, one can restart a simulation in a new directory (new compilation
   needed, first directory unmodified) with:

   ```sh
   snek-restart /path/of/the/simulation \
       --use-checkpoint 1 --end-time 0.005 --new-dir-results \
       --modify-params "params.nek.stat.av_step=1;"
   ```

   This method is particularly useful when one wants to change parameters with the
   `--modify-params` option.

[kth toolbox]: https://github.com/KTH-Nek5000/KTH_Toolbox
