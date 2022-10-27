<div align="center">

# Snek5000

[![PyPI](https://img.shields.io/pypi/v/snek5000)](https://pypi.org/project/snek5000/)
[![Tests Status](https://github.com/snek5000/snek5000/workflows/Tests/badge.svg)](https://github.com/snek5000/snek5000/actions?workflow=Tests)
[![Documentation Status](https://readthedocs.org/projects/snek5000/badge/?version=latest)](https://snek5000.readthedocs.io/en/latest/?badge=latest)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=snek5000_snek5000&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=snek5000_snek5000)
[![Code coverage](https://codecov.io/gh/snek5000/snek5000/branch/main/graph/badge.svg?token=WzGnN0dfbw)](https://codecov.io/gh/snek5000/snek5000)

<!-- badges -->

Python framework for Nek5000
</div>

**Documentation**: <https://snek5000.readthedocs.io/>

Snek5000 is a Python package which allows one to write [Fluidsim] solvers based
on the Fortran code [Nek5000] for the simulations. There are open-source
solvers (in particular [snek5000-phill], [snek5000-cbox] and [snek5000-tgv])
and it's not difficult to write your own solver (as shown in [this
tutorial](https://snek5000.readthedocs.io/en/latest/packaging.html)).

With a Snek5000-Fluidsim solver, it becomes very easy to

- launch/restart simulations with Python scripts
- load simulations, read the associated parameters/data and produce nice
  figures/movies

[Nek5000]: https://nek5000.mcs.anl.gov/
[Fluidsim]: https://fluidsim.readthedocs.io
[snek5000-phill]: https://github.com/snek5000/snek5000-phill
[snek5000-cbox]: https://github.com/snek5000/snek5000-cbox
[snek5000-tgv]: https://github.com/snek5000/snek5000/tree/main/docs/examples/snek5000-tgv

## Quick start

Install it as follows:

```sh
export NEK_SOURCE_ROOT="/path/to/Nek5000"
export PATH="$PATH:$NEK_SOURCE_ROOT/bin"

pip install snek5000
```

See here for [detailed installation instructions](https://snek5000.readthedocs.io/en/latest/install.html).

### Why Snek5000?

The [`snek5000` Python
API](https://snek5000.readthedocs.io/en/latest/_generated/snek5000.html) is
based on [fluidsim](https://fluidsim.readthedocs.io), which allows you to
launch/restart/load simulations with Python. For example, the [periodic hill
Nek5000 example](https://nek5000.github.io/NekDoc/tutorials/perhill.html) can
be launched with our [snek5000-phill] solver (installable with `pip install
snek5000-phill`) as follow:

```python
from phill.solver import Simul

params = Simul.create_default_params()

# modify parameters as needed, for example
params.output.sub_directory = "examples_snek_phill"
params.short_name_type_run = "readme"

params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.nek.general.num_steps = 10

...

# instantiate the object representing the simulation
sim = Simul(params)

# compile and launch the simulation (blocking)
sim.make.exec("run_fg")
```

A simulation directory is created automatically (with this example, something
like
`~/Sim_data/examples_snek_phill/phill_readme_12x10x8_V1.x1.x1._2022-10-27_15-21-58`).
Then, the simulation object can be recreated from this directory. An easy way
would be to go into this directory, start IPython with `ipython --matplotlib`
and run:

```python
from snek5000 import load

sim = load()

# get/print the simulation parameters from the object
sim.params

# few examples of various read and plots
sim.output.print_stdout.plot_dt()
sim.output.print_stdout.plot_nb_iterations()

sim.output.history_points.plot()
sim.output.history_points.coords
data = sim.output.history_points.load_1point(2)

sim.output.phys_fields.plot_hexa()
sim.output.phys_fields.animate("pressure", interactive=True)
sim.output.phys_fields.animate(
    "pressure", dt_frame_in_sec=0.1, save_file="my_great_movie.gif"
)
```

Check out the
[tutorials](https://snek5000.readthedocs.io/en/latest/tutorials.html) to learn
how to use Snek5000.

<details>
<summary>
<b>
Need more reasons to use snek5000?
</b>
</summary>

#### Advantages

- Saves you from the trouble in setting up multiple source files (`.box`, `.par`, `SIZE`)
- Checks for consistency of parameters
- Out of source builds and runs, which can be inspected or executed using the
  conventional `makenek` for debugging
- Avoid typos and human errors
- Better than Bash scripting like:

  ```sh
  # Build case
  cd src/phill/
  CASE="phill"
  echo "$CASE.box" | genbox
  mv -f box.re2 phill.re2
  echo "$CASE\n0.01" | genmap
  FFLAGS="-mcmodel=medium -march=native" CFLAGS="-mcmodel=medium -march=native" makenek
  cd -

  # Run case
  cd src/phill/
  nekmpi $CASE <nb_procs> # foreground
  nekbmpi $CASE <nb_procs> # background
  cd -

  # Clean
  makenek clean

  ```

- Use of [Snakemake](https://snakemake.readthedocs.io/en/stable/) which
  is similar to GNU Make, but allows one to blend bash and python scripting and
  uses simple YAML files for managing custom configurations of compilers and flags
  for different computers.

#### Disadvantages

- Yet another layer... with the possible associated bugs :-)
- Requires some basic knowledge of Python to use (*not really a big issue, to
  be honest*).
- Deep modification of solvers requires learning how
  [Snakemake](https://snakemake.readthedocs.io/en/stable/) functions and [how
  to write Jinja
  templates](https://jinja.palletsprojects.com/en/2.11.x/templates/) (which are
  not so hard, btw)

</details>

## Contributing

Contributions are welcome! You can help by testing out the code, filing issues
and submitting patches. See [contributing guidelines](CONTRIBUTING.md).
