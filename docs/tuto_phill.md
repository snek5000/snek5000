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

# Demo periodic hill (snek5000-phill solver)

<!-- #endregion -->

## Initialize and setup up simulation parameters (recap)

In the previous tutorial we saw how to install the packages and setup a simulation run.
Let us do it here in one step.

```{code-cell}
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

```{code-cell}
!ls {sim.path_run}
```

## Execute the simulation

To run the simulation we need to execute certain commands. These are described using
[snakemake](https://snakemake.rtfd.io) in the Snakefile. Let's look at the rules defined
in the Snakefile (which are nearly generic for any Nek5000 case).

```{code-cell}
sim.make.list()
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

<!-- #region tags=[] -->

### Debug mode

During development, it is useful to turn on the debug environment variable.

<!-- #endregion -->

```{code-cell}
import os
os.environ["SNEK_DEBUG"] = "1"
```

The equivalent of this in the shell command line would be `export SNEK_DEBUG=1`. By
doing so, snek5000 would:

- perform stricter compile time checks. See
  {func}`snek5000.util.smake.append_debug_flags`
- activate the code blocks under the preprocessing flag in Fortran sources
  `#ifdef DEBUG`

Now let's execute the simulation. We will use the script
[docs/examples/scripts/tuto_phill.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_phill.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill.py
```

In normal life, we would just execute this script with something like
`python tuto_phill.py`. However, in this notebook, we need a bit more code:

```{code-cell}
from subprocess import run, PIPE, STDOUT
from time import perf_counter

command = "python3 examples/scripts/tuto_phill.py"

print("Running the script tuto_phill.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
```

The simulation is done! Let's look at its output:

```{code-cell}
lines = [
    line for line in process.stdout.split("\n")
    if not line.endswith(", errno = 1")
]
print("\n".join(lines))
```

To "load the simulation", i.e. to recreate a simulation object, we now need to
extract from the output the path of the directory of the simulation:

```{code-cell}
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
path_run
```

Let's look at the files in the directory of the simulation

```{code-cell}
!ls {path_run}
```

In Snek5000, we have the notion of sessions (used for restarts) and some files
are saved in directories "session_00", "session_01", etc.

```{code-cell}
!ls {path_run}/session_00
```

## Versions used in this tutorial

```{code-cell}
!snek5000-info
```
