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

## Execute the simulation

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

```{note}

In real life, simulations are usually submitted with Snek5000 from a script and
we are going to call Snakemake from the Snek5000 Python API with a call similar
to `sim.make.exec("run_fg", nproc=2)` (as in the following example).

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

### Execution of the main script

Now let's execute the simulation. We will use the script
[docs/examples/scripts/tuto_phill.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_phill.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_phill.py
```

In normal life, we would just execute this script with something like
`python tuto_phill.py`. However, in this notebook, we need a bit more code:

```{code-cell} ipython3
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

### Snek5000 and Nek5000 log

The simulation is done! Let's look at its output:

```{code-cell} ipython3
lines = [
    line for line in process.stdout.split("\n")
    if not line.endswith(", errno = 1")
]
print("\n".join(lines))
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

## Loading the simulation

One can recreate a simulation object from the simulation directory.

```{code-cell} ipython3
from snek5000 import load

sim = load(path_run)
```

```{admonition} Quickly start IPython and load a simulation
The command `snek-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

## Read/plot state and stat files

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

## Versions used in this tutorial

```{code-cell} ipython3
!snek-info
```
