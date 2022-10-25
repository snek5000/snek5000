---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 100
---

<!-- #region tags=[] -->
# Part 2: Executing the simulation


<!-- #endregion -->

## Initialize and setup up simulation parameters (recap)


In the previous tutorial we saw how to install the packages and setup a simulation run. Let us do it here in one step.

```python
from phill.solver import Simul

params = Simul.create_default_params()
params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.oper.nproc_min = 2

params.nek.general.num_steps = 10
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 3
params.nek.stat.io_step = 10

sim = Simul(params)
```

```python
!ls {sim.path_run}
```

## Execute the simulation

To run the simulation we need to execute certain commands. These are described
using [snakemake](https://snakemake.rtfd.io) in the Snakefile. Let's look at
the rules defined in the Snakefile (which are nearly generic for any Nek5000
case).

```python
sim.make.list()
```

The rules in the Snakefile are either shell commands or Python code which
handle different parts of the build step, such as building a mesh (rule
`mesh`), compiling (rule `compile`) and running the simulation (rule `run` or
`run_fg`). The rules can be executed on by one by passing them as strings to
the [exec](snek5000.make.Make.exec) method of the `sim.make` object. The
default parameter is to do everything to run a simulation.

From a user's perspective the following rules are essential:
- `compile`: Only compile the executable
- `run`: Run the simulation in the background (non-blocking)
- `run_fg`: Run the simulation in the foreground (blocking, till the simulation is over / terminated)

<!-- #region tags=[] -->
### Debug mode

During development, it is useful to turn on the debug environment variable.
<!-- #endregion -->

```python
import os
os.environ["SNEK_DEBUG"] = "1"
```

The equivalent of this in the shell command line would be ``export
SNEK_DEBUG=1``. By doing so, snek5000 would:

- perform stricter compile time checks. See {func}`snek5000.util.smake.append_debug_flags`
- activate the code blocks under the preprocessing flag in Fortran sources `#ifdef DEBUG`



Now let's execute the simulation

```python
sim.make.exec?
```

```python
sim.make.exec('run_fg')
```

```python
!ls {sim.path_run}
```

The simulation is done!

## Versions used in this tutorial

```python
import snakemake
snakemake.__version__
```

```python
import snek5000
snek5000.__version__
```
```python
import phill
phill.__version__
```
