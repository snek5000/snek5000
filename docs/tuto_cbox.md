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
for the implementation. The simulation was executed as following:

```{code-cell}
import numpy as np

from snek5000_cbox.solver import Simul

params = Simul.create_default_params()

aspect_ratio = params.oper.aspect_ratio = 1.0
params.prandtl = 0.71

# The onset of oscillatory flow for aspect ratio 1.0 is at Ra_c = 1.825e8
params.Ra_side = 1.86e8

params.output.sub_directory = "examples_cbox/simple/SW"

params.oper.dim = 2
params.oper.nproc_min = 2

nb_elements = ny = 8
params.oper.ny = nb_elements
nx = params.oper.nx = int(nb_elements / aspect_ratio)
params.oper.nz = int(nb_elements / aspect_ratio)

Ly = params.oper.Ly
Lx = params.oper.Lx = Ly / aspect_ratio
Lz = params.oper.Lz = Ly / aspect_ratio

order = params.oper.elem.order = params.oper.elem.order_out = 8

params.oper.mesh_stretch_factor = 0.1  # zero means regular

params.short_name_type_run = f"Ra{params.Ra_side:.3e}_{nx*order}x{ny*order}"

# creation of the coordinates of the points saved by history points
n1d = 5
small = Lx / 10

xs = np.linspace(0, Lx, n1d)
xs[0] = small
xs[-1] = Lx - small

ys = np.linspace(0, Ly, n1d)
ys[0] = small
ys[-1] = Ly - small

coords = [(x, y) for x in xs for y in ys]

params.output.history_points.coords = coords
params.oper.max.hist = len(coords) + 1

params.nek.velocity.residual_tol = 1e-08
params.nek.pressure.residual_tol = 1e-05

params.nek.general.end_time = 800
params.nek.general.stop_at = "endTime"
params.nek.general.target_cfl = 2.0
params.nek.general.time_stepper = "BDF3"
params.nek.general.extrapolation = "OIFS"

params.nek.general.write_control = "runTime"
params.nek.general.write_interval = 50

params.output.history_points.write_interval = 30

sim = Simul(params)
sim.make.exec('run_fg', resources={"nproc": 2})
```

Here we load and process the output.

## Postprocessing

We can load the simulation:

```{code-cell}
from snek5000 import load

sim = load(sim.path_run)
```

then we are able to plot all the history points for one variable like $u_x$,

```{code-cell}
sim.output.history_points.plot(key='ux')

```

or just one history point:

```{code-cell}

sim.output.history_points.plot_1point(index_point=0, key='temperature', tmin=600, tmax=800)

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
print("Growth rate is:", growth_rate)
```

There is also the possibility to load to whole field file in
[xarray dataset](https://docs.xarray.dev/en/stable/index.html)

```{code-cell}

field = sim.output.phys_fields.load()

field.temperature.plot()
```

which makes postprocessing of data easier:

```{code-cell}
x_new = np.linspace(field.x[0], field.x[-1], field.x.size)
y_new = np.linspace(field.y[0], field.y[-1], field.y.size)

field = field.drop_duplicates(["x", "y"])
field = field.interp(x=x_new, y=y_new)

field.temperature.mean('x').plot()
```

## Versions used in this tutorial

```{code-cell}
import snakemake
snakemake.__version__
```

```{code-cell}
import snek5000
snek5000.__version__
```
