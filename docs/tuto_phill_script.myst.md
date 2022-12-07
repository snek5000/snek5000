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

# Demo periodic hill (`snek5000-phill` solver): running a simulation from a script

## Run a simulation by executing a script

Now let's execute the simulation. We will use the script
[docs/examples/scripts/tuto_phill.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_phill.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill.py
```

In normal life, we would just execute this script with something like
`python tuto_phill.py`.

```{code-cell} ipython3
command = "python3 examples/scripts/tuto_phill.py"
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

print("Running the script tuto_phill.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
lines = [
    line for line in process.stdout.split("\n")
    if not line.endswith(", errno = 1")
]
```

### Snek5000 and Nek5000 log

The simulation is done! We are going to look at its output (which is now in a variable
`lines`). However, be prepared to get something long because Nek5000 is very verbose.
For readability of this tutorial, the output is hidden by default (click to show it):

```{code-cell} ipython3
---
tags: [hide-output]
---
print("\n".join(lines))
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

### Other files produced during the simulation

Let's look at the files in the directory of the simulation

```{code-cell} ipython3
!ls {path_run}
```

In Snek5000, we have the notion of sessions (used for restarts) and some files are saved
in directories "session_00", "session_01", etc.

```{code-cell} ipython3
!ls {path_run}/session_00
```

## Load the simulation

One can recreate a simulation object from the simulation directory.

```{code-cell} ipython3
from snek5000 import load

sim = load(path_run)
```

```{admonition} Quickly start IPython and load a simulation
The command `snek-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

## Read and plot state and stat files as hexahedral data

We saw that the directory `session_00` contains a state file (`phill0.f00001`) and a
`sts` file (`stsphill0.f00001`).

Snek5000 has different methods to load these files. With the phill solver, the mesh is
not regular and we can only get the fields as hexahedral data.

```{code-cell} ipython3
hexa_data = sim.output.phys_fields.read_hexadata(index=-1)
hexa_data
```

```{code-cell} ipython3
sim.output.phys_fields.plot_hexa()
```

We can also do the same for the data produced by the KTH toolbox.

```{code-cell} ipython3
hexa_data_stat = sim.output.phys_fields.read_hexadata_stat(index=-1)
hexa_data_stat
```

The elements contain a `scal` array corresponding to the 44 fields computed by the KTH
toolbox (see
https://github.com/KTH-Nek5000/KTH_Toolbox/blob/master/tools/stat/field_list.txt).

```{code-cell} ipython3
hexa_data_stat.elem[0].scal.shape
```

```{code-cell} ipython3
sim.output.phys_fields.plot_hexa_stat(key="scalar 8", vmin=-0.4, vmax=0.4)
```
