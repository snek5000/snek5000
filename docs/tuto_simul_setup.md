---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 100
---

<!-- #region tags=[] -->
#  Part 1: Setting up the simulation

The [phill example](https://github.com/KTH-Nek5000/KTH_Examples/tree/master/phill_STAT) has been adapted for a workflow using snek5000 and pymech. Here we will show how a workflow looks like. To get started, we install everything we need:

```sh
python -m venv venv
source venv/bin/activate
pip install snek5000 pymech -e "git+https://github.com/snek5000/snek5000-phill#egg=phill"
```

```{note}
The repository `snek5000-phill` provides a Python package `phill` - the same
name as the `usr` files. More on packaging Nek5000 files can be found in the
{ref}`packaging tutorial <packaging>`.
```
<!-- #endregion -->

## Initialize and setup up simulation parameters

```{code-cell}
from phill.solver import Simul

params = Simul.create_default_params()
```

The `params` object gives you a consolidated view of the parameters which are spread out in a typical Nek5000 case into `.par`, `.box` and `SIZE` file.  Already we seen that the parameters are more verbose, easier to understand. As a bonus, some parameters which depend on others are automatically set. For example, see {py:mod}`snek5000.operators`.

Now let us take a look at all the compilation parameters that we can modify. In a console the params would also output as follows:

```{code-cell}
print(params)
```

One can print some help about some parameters. For example, for `params.oper`:

```{code-cell}
params.oper._print_docs()
```

The parameters can be modified. For instance, let us tweak the number of elements, time-stepping and I/O parameters

```python
# This affects both the box and SIZE files
params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.oper.nproc_min = 2

# This affects the par file
params.nek.velocity.residual_tol = 1e-8
params.nek.pressure.residual_tol = 1e-6 
params.nek.general.num_steps = 10
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 3
params.nek.stat.io_step = 10
```

Now initialize the simulation. This would copy the files based on the templates we have specified.

```{code-cell}
sim = Simul(params)
sim.path_run
```

```{code-cell}
!ls {sim.path_run}
```

<!-- #region tags=[] -->
## Versions used in this tutorial
<!-- #endregion -->

```{code-cell}
import snakemake
snakemake.__version__
```

```{code-cell}
import snek5000
snek5000.__version__
```
```{code-cell}
import phill
phill.__version__
```
