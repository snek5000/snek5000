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

# Demo Taylor-Green vortex (`snek5000-tgv` solver)

Snek5000 repository contains a
[simple example solver](https://github.com/snek5000/snek5000/tree/main/docs/examples/snek5000-tgv)
for the Taylor-Green vortex flow. We are going to show how it can be used on a very
small and short simulation.

## Run a simulation by executing a script

We will run the simulation by executing the script
[docs/examples/scripts/tuto_tgv.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_tgv.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_tgv.py
```

In normal life, we would just execute this script with something like
`python tuto_tgv.py`.

```{code-cell} ipython3
command = "python3 examples/scripts/tuto_tgv.py"
```

However, in this notebook, we need a bit more code. How we execute this command is very
specific to these tutorials written as notebooks so you can just look at the output of
this cell.

```{code-cell} ipython3
---
tags: [hide-input]
---
from subprocess import run, PIPE, STDOUT
from time import perf_counter

print("Running the script tuto_tgv.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = process.stdout.split("\n")
```

```{code-cell} ipython3
---
tags: [remove-cell]
---
# filter to remove useless warnings
lines = [line for line in lines if not line.endswith(", errno = 1")]
```

The simulation is done! We are going to look at its output (which is now in a variable
`lines`). However, be prepared to get something long because Nek5000 is very verbose.
For readability of this tutorial, the output is hidden by default (click to show it).

Let us first look at the first lines, until the beginning of the time stepping:

```{code-cell} ipython3
---
tags: [hide-output]
---
index_step2 = 0
for line in lines:
    if line.startswith("Step      2, t= "):
        break
    index_step2 += 1

print("\n".join(lines[:index_step2+20]))
```

And then at the last lines, from the end of the time stepping:

```{code-cell} ipython3
---
tags: [hide-output]
---
index_final_step = 0
for line in lines[::-1]:
    if line.startswith(" Final time step ="):
        break
    index_final_step -= 1

print("\n".join(lines[index_final_step-10:]))
```

To "load the simulation", i.e. to recreate a simulation object, we now need to extract
from the output the path of the directory of the simulation. This is also very specific
to these tutorials, so you don't need to focus on this code. In real life, we can just
read the log to know where the data has been saved.

```{code-cell} ipython3
---
tags: [hide-input]
---
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
```

```{code-cell} ipython3
path_run
```

## Load the simulation

We can now load the simulation and process the output.

<!-- #endregion -->

```{code-cell} ipython3
from snek5000 import load

sim = load(path_run)
```

```{admonition} Quickly start IPython and load a simulation
The command `snek-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

+++

## How long was the run?

`snek5000-tgv` saves a file `remaining_clock_time.csv` during the simulation. It can be
read manually,

```{code-cell} ipython3
!cat {path_run}/remaining_clock_time.csv
```

and there is also an object `sim.output.remaining_clock_time` to load and plot these
data (which is especially useful during the simulation!):

```{code-cell} ipython3
sim.output.remaining_clock_time.plot()
```

## Parse, load and plot information contained in the Nek5000 log

The object `sim.output.print_stdout` (see
{class}`snek5000.output.print_stdout.PrintStdOut`) contains utilities to represent
information contained in the Nek5000 log. For example, one can do:

```{code-cell} ipython3
log_data = sim.output.print_stdout.load()
log_data
```

and plot useful figures with

```{code-cell} ipython3
sim.output.print_stdout.plot_dt_cfl()
```

and

```{code-cell} ipython3
sim.output.print_stdout.plot_nb_iterations()
```

## Visualize spatial means data

In subroutine `userchk` of `tgv.usr.f`, the time stamp, kinetic energy and enstrophy are
output in a file `spatial_means.csv`. The data can be loaded with

```{code-cell} ipython3
df = sim.output.spatial_means.load()
df.head()
```

### Reference data

```{code-cell} ipython3
import pandas as pd

ref = pd.read_csv(
    "examples/snek5000-tgv/ref_data_spectral_code.csv",
    sep=" ",
    names=("time", "ref:energy", "ref:dE/dt", "ref:enstrophy"),
    comment="#"
)
ref.head()
```

### Result

```{code-cell} ipython3
sim.output.spatial_means.plot(logy=True, colormap="Accent")

import matplotlib.pyplot as plt

ax = plt.gca()
ref.plot(
    "time",
    ["ref:energy", "ref:enstrophy"],
    ax=ax,
    style="--",
    logy=True,
    colormap="Accent"
)
ax.set(
    title=f"Taylor-Green vortex: evolution of K.E. and enstrophy. Re={-sim.params.nek.velocity.viscosity}"
)
ax.figure.tight_layout()
```

### Restart to run further

We see that our first simulation was clearly too short. We can use the command line tool
`snek-restart` (see the [How to page dedicated to restart](./how-to/restart.md)) to
continue the simulation from the last saved file (`--use-start-from -1`):

```{code-cell} ipython3
print("Running the restart command...")
t_start = perf_counter()
lines = !snek-restart {sim.path_run} --use-start-from -1 --add-to-end-time 4
print(f"Command executed in {perf_counter() - t_start:.2f} s")
```

```{code-cell} ipython3
---
tags: [remove-cell]
---
# filter to remove useless warnings
lines = [line for line in lines if not line.endswith(", errno = 1")]
```

Let's look at the end of the output of this command:

```{code-cell} ipython3
---
tags: [hide-output]
---
print("\n".join(lines[-120:]))
```

The results of the new simulation were saved in a directory `session_01`

```{code-cell} ipython3
sorted(p.name for p in sim.path_run.iterdir())
```

which contains:

```{code-cell} ipython3
sorted(p.name for p in (sim.path_run / "session_01").iterdir())
```

The log files of the simulations are saved in `logs`:

```{code-cell} ipython3
paths_log = sorted(sim.path_run.glob("logs/*"))
[p.name for p in paths_log]
```

Let's get the spatial means data from the second simulation:

```{code-cell} ipython3
df_new = sim.output.spatial_means.load()
df_new = df_new[df_new.time > df.time.max()]
```

We finally plot the new points!

```{code-cell} ipython3
df_new.plot("time", ["energy", "enstrophy"], ax=ax, logy=True, colormap="Accent", style=".-")
ax.figure
```

Note that we use for this tutorial very small and coarse simulations, which explain the
differences between our results and the reference!

Let us see what gives the `remaining_clock_time` plot after the second simulation:

```{code-cell} ipython3
sim.output.remaining_clock_time.plot()
```
