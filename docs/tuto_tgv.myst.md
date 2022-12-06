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

# Demo Taylor-Green vortex (snek5000-tgv solver)

Snek5000 repository contains a
[simple example solver](https://github.com/snek5000/snek5000/tree/main/docs/examples/snek5000-tgv)
for the Taylor-Green vortex flow. We are going to show how it can be used on a very
small and short simulation.

## Run the simulation

We will run the simulation by executing the script
[docs/examples/scripts/tuto_tgv.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_tgv.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_tgv.py
```

In normal life, we would just execute this script with something like
`python tuto_tgv.py`. However, in this notebook, we need a bit more code:

```{code-cell} ipython3
from subprocess import run, PIPE, STDOUT
from time import perf_counter

command = "python3 examples/scripts/tuto_tgv.py"

print("Running the script tuto_tgv.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
```

The script has now been executed. Let's look at its output:

```{code-cell} ipython3
lines = [
    line for line in process.stdout.split("\n")
    if not line.endswith(", errno = 1")
]

index_step2 = 0
for line in lines:
    if line.startswith("Step      2, t= "):
        break
    index_step2 += 1

print("\n".join(lines[:index_step2+20]))
```

```{code-cell} ipython3
index_final_step = 0
for line in lines[::-1]:
    if line.startswith(" Final time step ="):
        break
    index_final_step -= 1

print("\n".join(lines[index_final_step-10:]))
```

To "load the simulation", i.e. to recreate a simulation object, we now need to extract
from the output the path of the directory of the simulation:

```{code-cell} ipython3
path_run = None
for line in lines:
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
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

## Visualize raw data via `sim.output.print_stdout`

In subroutine `userchk` of `tgv.usr.f`, the time stamp, kinetic energy and enstrophy are
output into standard output, with a keyword `monitor` at the end of the line. We can use
regular expressions to extract these lines. If you are new to regular expressions, this
website can help you <https://regex101.com/>.

```{code-cell} ipython3
import re

monitor = re.findall('(.*)monitor$', sim.output.print_stdout.text, re.MULTILINE)
monitor
```

It is also possible to achieve the same using Python's string manipulation and list
comprehension:

```{code-cell} ipython3
monitor = [
    line[:-len("monitor")]  # Or in Python >= 3.9, line.removesuffix("monitor")
    for line in sim.output.print_stdout.text.splitlines()
    if line.endswith("monitor")
]
```

```{code-cell} ipython3
import pandas as pd

df = pd.DataFrame(
    ((float(value) for value in line.split()) for line in monitor),
    columns=("time", "energy", "enstrophy")
)
df.head()
```

### Reference data

```{code-cell} ipython3
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
ax = df.plot("time", ["enstrophy", "energy"], logy=True, colormap="Accent")
ref.plot(
    "time",
    ["ref:enstrophy", "ref:energy"],
    ax=ax,
    style="--",
    logy=True,
    colormap="Accent"
)
ax.set(
    title=f"Taylor-Green vortex: evolution of K.E. and enstrophy. Re={-sim.params.nek.velocity.viscosity}"
);
```

### Restart to run further

We see that our first simulation was clearly too short. We can use the command line tool
`snek-restart` (see the [How to page dedicated to restart](./how-to/restart.md)) to
continue the simulation from the last saved file (`--use-start-from -1`):

```{code-cell} ipython3
lines = !snek-restart {sim.path_run} --use-start-from -1 --add-to-end-time 4
```

Let's look at the end of the output of this command:

```{code-cell} ipython3
# filter to remove useless warnings
lines = [line for line in lines if not line.endswith(", errno = 1")]
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

Let's get the "monitor" points from the log of the second simulation:

```{code-cell} ipython3
path_log_new_simul = paths_log[-1]
monitor = [
    line[:-len("monitor")]  # Or in Python >= 3.9, line.removesuffix("monitor")
    for line in path_log_new_simul.read_text().splitlines()
    if line.endswith("monitor")
]
df_new = pd.DataFrame(
    ((float(value) for value in line.split()) for line in monitor),
    columns=("time", "energy", "enstrophy")
)
```

We finally plot the new points!

```{code-cell} ipython3
df_new.plot("time", ["enstrophy", "energy"], ax=ax, logy=True, colormap="Accent", style=".-")
ax.figure
```

Note that we use for this tutorial very small and coarse simulations, which explain the
differences between our results and the reference!

## Versions used in this tutorial

```{code-cell} ipython3
!snek-info
```
