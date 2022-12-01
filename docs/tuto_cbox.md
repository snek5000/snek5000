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

# Demo sidewall convection (snek5000-cbox solver)

<!-- #endregion -->

## Initialize and setup simulation parameters

This example is based on
[this study](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/abs/from-onset-of-unsteadiness-to-chaos-in-a-differentially-heated-square-cavity/617F4CB2C23DD74C3D0CB872AE7C0045).
The configuration is a square cavity. The control parameters are Prandtl $= 0.71$ and
Rayleigh $= 2 \times 10^{8}$. The mesh size is $64 \times 64$. We want to have $25$
probes (history points) to record the variable signals. We will use these probe signals
in monitoring and postprocessing of the simulation. See
[this example](https://github.com/snek5000/snek5000-cbox/blob/gh-actions/doc/examples/run_side_short.py)
for the implementation.

The simulation will be carried out with the script
[docs/examples/scripts/tuto_cbox.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_cbox.py).
Note that this script is more complicated than for the previous tutorial. Here, we want
to demonstrate that it is possible to check what happen in the simulation from Python
and to stop the simulation depending on its outputs. We know that for moderate Rayleigh
number, the side wall convection in a box first reach a quasi-steady state from which
emerges an oscillatory instability. Here, we want to stop the simulation as soon as the
linear instability starts to saturate, i.e. as soon as the growth of the unstable mode
becomes slower than exponential.

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_cbox.py
```

In normal life, we would just execute this script with something like
`python tuto_cbox.py`. However, in this notebook, we need a bit more code:

```{code-cell} ipython3
from subprocess import run, PIPE, STDOUT
from time import perf_counter

command = "python3 examples/scripts/tuto_cbox.py"

print("Running the script tuto_cbox.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
```

The script has now been executed. Let's look at its output.

```{code-cell} ipython3
print(process.stdout)
```

To "load the simulation", i.e. to recreate a simulation object, we now need to extract
from the output the path of the directory of the simulation:

```{code-cell} ipython3
path_run = None
for line in process.stdout.split("\n"):
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
path_run
```

We can now read the Nek5000 log file.

```{code-cell} ipython3
from pathlib import Path

path_log = Path(path_run) / "cbox.log"
lines = path_log.read_text().split("\n")

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
    if line.startswith("Step") and ", t= " in line:
        break
    index_final_step -= 1
print("\n".join(lines[index_final_step-10:]))
```

## Postprocessing

We can load the simulation:

```{code-cell} ipython3
from snek5000 import load

sim = load(path_run)
```

```{admonition} Quickly start IPython and load a simulation
The command `snek-ipy-load` can be used to start a IPython session and load the
simulation saved in the current directory.
```

Then we are able to plot all the history points for one variable (here the temperature),

```{code-cell} ipython3
sim.output.history_points.plot(key='temperature');
```

```{code-cell} ipython3
ax = sim.output.history_points.plot(key='temperature')
ax.set_xlim(left=300)
ax.set_ylim([0.2, 0.36]);
```

or just one history point:

```{code-cell} ipython3
ax = sim.output.history_points.plot_1point(
  index_point=12, key='temperature', tmin=300, tmax=800
)

coords, df = sim.output.history_points.load()

import numpy as np
from scipy import stats
from scipy.signal import argrelmax

df_point = df[df.index_points == 12]
times = df_point["time"].to_numpy()
signal = df_point["temperature"].to_numpy()

cond = times > 400
times = times[cond]
signal = signal[cond]

indices_maxima = argrelmax(signal)
times_maxima = times[indices_maxima]
signal_maxima = signal[indices_maxima]

cond = signal_maxima > 0
times_maxima = times_maxima[cond]
signal_maxima = signal_maxima[cond]

ax.plot(times_maxima, signal_maxima, "xr");
```

Moreover, we can also compute an approximation of the growth rate:

```{code-cell} ipython3
try:
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        times_maxima, np.log(abs(signal_maxima))
    )
except ValueError:
    pass
else:
    growth_rate = slope
    print(f"The growth rate is {growth_rate:.2e}")
```

## Load the flow field as xarray dataset

There is also the possibility to load to whole field file in
[xarray dataset](https://docs.xarray.dev/en/stable/index.html)

```{code-cell} ipython3
field = sim.output.phys_fields.load()

field.temperature.plot();
```

which makes postprocessing of data easier:

```{code-cell} ipython3
x_new = np.linspace(field.x[0], field.x[-1], field.x.size)
y_new = np.linspace(field.y[0], field.y[-1], field.y.size)

field = field.drop_duplicates(["x", "y"])
field = field.interp(x=x_new, y=y_new)

field.temperature.mean('x').plot();
```

## Versions used in this tutorial

```{code-cell} ipython3
!snek-info
```
