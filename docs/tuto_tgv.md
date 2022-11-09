---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 600
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

```{code-cell}
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

```{code-cell}
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

```{code-cell}
index_final_step = 0
for line in lines[::-1]:
    if line.startswith(" Final time step ="):
        break
    index_final_step -= 1

print("\n".join(lines[index_final_step-10:]))
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
```

## Load the simulation

We can now load the simulation and process the output.

<!-- #endregion -->

```{code-cell}
from snek5000 import load

sim = load(path_run)
```

## Visualize raw data via `sim.output.print_stdout`

In subroutine `userchk` of `tgv.usr.f`, the time stamp, kinetic energy and enstrophy are
output into standard output, with a keyword `monitor` at the end of the line. We can use
regular expressions to extract these lines. If you are new to regular expressions, this
website can help you <https://regex101.com/>.

```{code-cell}
import re

monitor = re.findall('(.*)monitor$', sim.output.print_stdout.text, re.MULTILINE)
monitor
```

It is also possible to achieve the same using Python's string manipulation and list
comprehension:

```{code-cell}
monitor = [
    line[:-len("monitor")]  # Or in Python >= 3.9, line.removesuffix("monitor")
    for line in sim.output.print_stdout.text.splitlines()
    if line.endswith("monitor")
]
```

```{code-cell}
import pandas as pd

df = pd.DataFrame(
    ((float(value) for value in line.split()) for line in monitor),
    columns=("time", "energy", "enstrophy")
)
df.head()
```

### Reference data

```{code-cell}
ref = pd.read_csv(
    "examples/snek5000-tgv/ref_data_spectral_code.csv",
    sep=" ",
    names=("time", "ref:energy", "ref:dE/dt", "ref:enstrophy"),
    comment="#"
)
ref.head()
```

### Result

```{code-cell} tags=[]
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
