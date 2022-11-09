---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 300
---

<!-- #region tags=[] -->

# Demo sidewall convection (snek5000-cbox solver)

<!-- #endregion -->

## Initialize and setup simulation parameters

This example is based on
[this study](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/abs/from-onset-of-unsteadiness-to-chaos-in-a-differentially-heated-square-cavity/617F4CB2C23DD74C3D0CB872AE7C0045).
The configuration is a square cavity. The control parameters are Prandtl $= 0.71$ and
Rayleigh $= 1.86 \times 10^{8}$. The mesh size is $64 \times 64$. We want to have $25$
probes (history points) to record the variable signals. We will use these probe signals
in monitoring and postprocessing of the simulation. See
[this example](https://github.com/snek5000/snek5000-cbox/blob/gh-actions/doc/examples/run_side_short.py)
for the implementation. The simulation will be carried out with the script
[docs/examples/scripts/tuto_cbox.py](https://github.com/snek5000/snek5000/tree/main/docs/examples/scripts/tuto_cbox.py),
which contains:

```{eval-rst}
.. literalinclude:: ./examples/scripts/tuto_cbox.py
```

In normal life, we would just execute this script with something like
`python tuto_cbox.py`. However, in this notebook, we need a bit more code:

```{code-cell}
from subprocess import run, PIPE, STDOUT
from time import perf_counter

command = "python3 examples/scripts/tuto_cbox.py"

print("Running the script tuto_box.py... (It can take few minutes.)")
t_start = perf_counter()
process = run(
    command.split(), check=True, text=True, stdout=PIPE,  stderr=STDOUT
)
print(f"Script executed in {perf_counter() - t_start:.2f} s")
```

The script has now been executed. Let's look at its output.

```{code-cell}
lines = process.stdout.split("\n")
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
for line in process.stdout.split("\n"):
    if "path_run: " in line:
        path_run = line.split("path_run: ")[1].split(" ", 1)[0]
        break
if path_run is None:
    raise RuntimeError
path_run
```

## Postprocessing

We can load the simulation:

```{code-cell}
from snek5000 import load

sim = load(path_run)
```

then we are able to plot all the history points for one variable like $u_x$,

```{code-cell}
sim.output.history_points.plot(key='ux');
```

or just one history point:

```{code-cell}
sim.output.history_points.plot_1point(
  index_point=0, key='temperature', tmin=600, tmax=800
);
```

Also we can load the history points data to compute growth rate:

```{code-cell}
import numpy as np
from scipy import stats
from scipy.signal import argrelmax

coords, df = sim.output.history_points.load()
df_point = df[df.index_points == 12]
time = df_point["time"].to_numpy()
ux = df_point["ux"].to_numpy()

indx = np.where(time > 700)[0][0]
time = time[indx:]
ux = ux[indx:]
signal = ux

arg_local_max = argrelmax(signal)
time_local_max = time[arg_local_max]
signal_local_max = signal[arg_local_max]

slope, intercept, r_value, p_value, std_err = stats.linregress(
    time_local_max, np.log(signal_local_max)
)

growth_rate = slope
print(f"the growth rate is {growth_rate:.2f}")
```

There is also the possibility to load to whole field file in
[xarray dataset](https://docs.xarray.dev/en/stable/index.html)

```{code-cell}

field = sim.output.phys_fields.load()

field.temperature.plot();
```

which makes postprocessing of data easier:

```{code-cell}
x_new = np.linspace(field.x[0], field.x[-1], field.x.size)
y_new = np.linspace(field.y[0], field.y[-1], field.y.size)

field = field.drop_duplicates(["x", "y"])
field = field.interp(x=x_new, y=y_new)

field.temperature.mean('x').plot();
```

## Versions used in this tutorial

```{code-cell}
!snek5000-info
```
