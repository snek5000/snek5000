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

<!-- #region tags=[] -->

# Second step with `snek5000-phill`: Snakemake rules

<!-- #endregion -->

## Initialization of the simulation (recap)

In the previous tutorial [](../tuto_phill_setup.md), we saw how to setup a simulation
run. Let us do it here in one step.

```{code-cell} ipython3
from phill.solver import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_snek/tuto"
params.oper.nx = 6
params.oper.ny = 5
params.oper.nz = 4
params.oper.elem.order = params.oper.elem.order_out = 10

params.oper.nproc_min = 2

params.nek.general.num_steps = 10
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 3
params.nek.stat.io_step = 10

sim = Simul(params)
```

We recall that this instanciation of the class `Simul` creates the simulation directory
on the disk with the following files:

```{code-cell} ipython3
!ls {sim.path_run}
```

## Execute the simulation with Snakemake rules

### Snakemake rules

To run the simulation we need to execute certain commands. These are described using
[snakemake](https://snakemake.rtfd.io) in the Snakefile. Let's look at the rules defined
in the Snakefile (which are nearly generic for any Nek5000 case).

```{code-cell} ipython3
sim.make.list();
```

The rules in the Snakefile are either shell commands or Python code which handle
different parts of the build step, such as building a mesh (rule `mesh`), compiling
(rule `compile`) and running the simulation (rule `run` or `run_fg`). The rules can be
executed on by one by passing them as strings to the [exec](snek5000.make.Make.exec)
method of the `sim.make` object. The default parameter is to do everything to run a
simulation.

From a user's perspective the following rules are essential:

- `compile`: Only compile the executable
- `run`: Run the simulation in the background (non-blocking)
- `run_fg`: Run the simulation in the foreground (blocking, till the simulation is over
  / terminated)

Hence, the most standard method to launch a simulation with Snek5000 is to call

```python
sim.make.exec("run_fg", nproc=2)
```

In the next tutorial [](../tuto_phill_script.md), we will do it from a script and see
what happens, but we can already guess that all the Snakemake rules necessary for the
simulation are going to be executed.

```{note}

In real life, simulations are usually submitted with Snek5000 from a script and
we are going to call Snakemake with the [exec](snek5000.make.Make.exec)
method.

However, there is also a command `snek-make` that can be run from the
simulation directory to list and invoke the Snakemake rules. See `snek-make -h`
and `snek-make -l`.

```

<!-- #region tags=[] -->

### Debug mode

During development, it can be useful to turn on the debug environment variable which can
be done in Python with:

<!-- #endregion -->

```python
import os
os.environ["SNEK_DEBUG"] = "1"
```

The equivalent of this in the shell command line would be `export SNEK_DEBUG=1`. By
doing so, snek5000 would:

- perform stricter compile time checks. See
  {func}`snek5000.util.smake.append_debug_flags`
- activate the code blocks under the preprocessing flag in Fortran sources
  `#ifdef DEBUG`
