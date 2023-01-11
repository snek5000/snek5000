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

# First step with `snek5000-phill`: setting up a simulation

## Installation of `snek5000-phill`

The
[Nek5000 phill example](https://github.com/KTH-Nek5000/KTH_Examples/tree/master/phill_STAT)
(`phill` means periodic hill) has been adapted for a workflow using Snek5000. We created
[a small Python project called `snek5000-phill`](https://pypi.org/project/snek5000-phill/)
using the Snek5000 API to define the `phill` case. In this tutorial and in the tutorials
[](../tuto_phill_make.md) and [](../tuto_phill_script.md), we will show how this solver
can be used. Let's first recall that the installation procedure looks like this:

```sh
export NEK_SOURCE_ROOT="/path/to/Nek5000"
python -m venv venv
source venv/bin/activate
pip install snek5000-phill
```

```{note}
The repository `snek5000-phill` provides a Python package `phill` - the same
name as the `usr` files. More on packaging Nek5000 files can be found in the
{ref}`packaging tutorial <packaging>`.
```

<!-- #endregion -->

## `params` object for simulation parameters

### Creating the `params` object containing default parameters

```{code-cell}
from phill.solver import Simul

params = Simul.create_default_params()
```

The `params` object gives you a consolidated view of the parameters which are spread out
in a typical Nek5000 case into `.par`, `.box` and `SIZE` file. We will see that the
parameters are more verbose and easier to understand. As a bonus, some Nek5000
parameters which depend on others are automatically set. For example, see
{py:mod}`snek5000.operators`.

### Studying the parameters (print and get help)

Now let us take a look at the parameters defining a simulation. In a IPython or Jupyter
console, the `params` object would also output as follows:

```{code-cell}
print(params)
```

One can also print only one section:

```{code-cell}
print(params.nek.general)
```

or alternatively, with the method `_print_as_code` (useful for copy-pasting):

```{code-cell}
params.nek.general._print_as_code()
```

Note that it is easy to print some help about some parameters:

```{code-cell}
params.oper._print_docs()
```

```{warning}
We will see later that the same object `params` can also be obtained from a simulation
object (with `sim.params`), but the help on the parameters can only be printed from
`params` objects obtained from `Simul.create_default_params()`.
```

### Modifying the parameters

Of course, the parameters can be modified. For instance, let us tweak the number of
elements, time-stepping and I/O parameters

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

## Creation of the simulation object and directory

Now let's create the simulation object (We usually use the name `sim`.):

```{code-cell}
sim = Simul(params)
```

Information is given about the structure of the `sim` object (which has attributes
`sim.oper`, `sim.output` and `sim.make` corresponding to different aspects of the
simulation) and about the creation of some files.

We see that a directory has been created with all the files (`.usr`, `.par`, `.box`,
`SIZE`, etc.) necessary to compile and run the simulation. Note that these files has
been created based on templates files in the `snek5000` and `phill` packages. The path
towards the simulation directory is:

```{code-cell}
sim.path_run
```

Let's check that the `.par`, `.box` and `SIZE` files are present:

```{code-cell}
!ls {sim.path_run}
```

```{note}
The path of the directory where the simulation directories are saved can be
changed through the environment variable `FLUIDSIM_PATH`.
```
