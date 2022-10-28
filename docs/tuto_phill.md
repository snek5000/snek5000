---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 200
---

<!-- #region tags=[] -->
# Demo periodic hill (snek5000-phill)

<!-- #endregion -->

## Initialize and setup up simulation parameters (recap)


In the previous tutorial we saw how to install the packages and setup a simulation run. Let us do it here in one step.

```{code-cell}
from phill.solver import Simul

params = Simul.create_default_params()
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

```{code-cell}
!ls {sim.path_run}
```

## Execute the simulation

To run the simulation we need to execute certain commands. These are described
using [snakemake](https://snakemake.rtfd.io) in the Snakefile. Let's look at
the rules defined in the Snakefile (which are nearly generic for any Nek5000
case).

```{code-cell}
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

```{code-cell}
import os
os.environ["SNEK_DEBUG"] = "1"
```

The equivalent of this in the shell command line would be ``export
SNEK_DEBUG=1``. By doing so, snek5000 would:

- perform stricter compile time checks. See {func}`snek5000.util.smake.append_debug_flags`
- activate the code blocks under the preprocessing flag in Fortran sources `#ifdef DEBUG`



Now let's execute the simulation

```{code-cell}
sim.make.exec?
```

```{code-cell}
sim.make.exec('run_fg', resources={"nproc": 2})
```

```{code-cell}
!ls {sim.path_run}
```

The simulation is done!

## Versions used in this tutorial

```{code-cell}
import snakemake
snakemake.__version__
```

```{code-cell}
import snek5000
snek5000.__version__
```
```{code-cell}
import phill
phill.__version__
```
