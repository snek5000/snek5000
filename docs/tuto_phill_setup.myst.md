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

# First steps with snek5000-phill: setting up the simulation

The
[Nek5000 phill example](https://github.com/KTH-Nek5000/KTH_Examples/tree/master/phill_STAT)
has been adapted for a workflow using snek5000. Here we will show how this workflow
looks like. To get started, we install everything we need:

```sh
python -m venv venv
source venv/bin/activate
pip install "snek5000-phill @ git+https://github.com/snek5000/snek5000-phill.git"
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

The `params` object gives you a consolidated view of the parameters which are spread out
in a typical Nek5000 case into `.par`, `.box` and `SIZE` file. Already we seen that the
parameters are more verbose, easier to understand. As a bonus, some parameters which
depend on others are automatically set. For example, see {py:mod}`snek5000.operators`.

Now let us take a look at all the compilation parameters that we can modify. In a
console the params would also output as follows:

```{code-cell}
print(params)
```

One can also print only one section:

```{code-cell}
print(params.nek.general)
```

and print some help about some parameters:

```{code-cell}
params.oper._print_docs()
```

```{warning}
The same object `params` can also be obtained from a simulation object (with
`sim.params`), but the help on the parameters can only be printed from `params`
objects obtained from `Simul.create_default_params()`.
```

The parameters can be modified. For instance, let us tweak the number of elements,
time-stepping and I/O parameters

```python
# This affects both the .box and SIZE files
params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

# This affects the .par file
params.nek.velocity.residual_tol = 1e-8
params.nek.pressure.residual_tol = 1e-6
params.nek.general.num_steps = 10
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 3
params.nek.stat.io_step = 10
```

Now let's initialize the simulation. This is going to create the files based on the
templates we have specified.

```{code-cell}
sim = Simul(params)
```

A directory has been created with all the files necessary to compile and run the
simulation:

```{code-cell}
sim.path_run
```

Let's check that the .par, .box and SIZE file are present:

```{code-cell}
!ls {sim.path_run}
```

<!-- #region tags=[] -->

## Versions used in this tutorial

<!-- #endregion -->

```{code-cell}
!snek-info
```
