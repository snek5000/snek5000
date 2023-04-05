# How to set adaptive time step in Nek5000

In the Nek5000 documentation, `variableDT` in `GENERAL` keys in [`.par` file](https://nek5000.github.io/NekDoc/problem_setup/case_files.html#parameter-file-par) is used to control whether the step size will be adjusted to match the `targetCFL`.

In Snek5000, you can enable this feature by setting `params.nek.general.variable_dt` to `True`.

For example, in the script below, we set `variable_dt` as `True`, which subsequently leads to an adaptive time step based on the `target_cfl`:

```{code-block} python
---
emphasize-lines: 20-21
---
from snek5000_tgv.solver import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_snek/tuto"

params.oper.nx = params.oper.ny = params.oper.nz = 8
params.oper.elem.order = params.oper.elem.order_out = 8
params.oper.nproc_min = 2

params.nek.velocity.residual_tol = 1e-07
params.nek.pressure.residual_tol = 1e-05

params.nek.general.write_control = "runTime"
params.nek.general.write_interval = 2.0

params.output.spatial_means.write_interval = 0.5

params.nek.general.end_time = 10
params.nek.general.dt = 1
params.nek.general.target_cfl = 1.4
params.nek.general.variable_dt = True
params.nek.general.extrapolation = "OIFS"

sim = Simul(params)
sim.make.exec("run_fg", nproc=2)
```
