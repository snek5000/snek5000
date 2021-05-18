<div align="center">

# snek5000

[![PyPI](https://img.shields.io/pypi/v/snek5000)](https://pypi.org/project/snek5000/)
[![Tests Status](https://github.com/exabl/snek5000/workflows/Tests/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Tests)
[![Documentation Status](https://readthedocs.org/projects/snek5000/badge/?version=latest)](https://snek5000.readthedocs.io/en/latest/?badge=latest)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=exabl_snek5000&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=exabl_snek5000)
[![Code coverage](https://codecov.io/gh/exabl/snek5000/branch/master/graph/badge.svg?token=WzGnN0dfbw)](https://codecov.io/gh/exabl/snek5000)

Python framework for Nek5000
</div>

**Warning:** This framework is experimental and of beta-quality.

**Documentation**: https://snek5000.readthedocs.io/

## Installation

Install it as follows:

```sh
export NEK_SOURCE_ROOT="/path/to/Nek5000"
export PATH="$PATH:$NEK_SOURCE_ROOT/bin"

pip install snek5000
```

### Why snek5000?

The [`snek5000` Python
API](https://snek5000.readthedocs.io/en/latest/_generated/snek5000.html) is based on
[fluidsim](https://fluidsim.readthedocs.io), which allows you to launch a
simulation using scripts. For example the [periodic hill
example](https://github.com/exabl/snek5000-phill) can be launched as.

```python
from phill.solver import Simul

params = Simul.create_default_params()

# modify parameters as needed

sim = Simul(params)
sim.make.exec()  # by default starts a run
sim.make.exec(["mesh", "compile"])  # run rules in order
sim.make.exec(["run"], dryrun=True)  # simulate simulation
sim.make.exec(["run"])  # actual simulation
```

Check out the
[tutorials](https://snek5000.readthedocs.io/en/latest/tutorials.html) to learn
how to use `snek5000`.

<details>
<summary>
<b>
Need more reasons to use snek5000?
</b>
</summary>

#### Advantages

- Saves you from the trouble in setting up multiple source files (`.box`, `.par`, `SIZE`)
- Checks for consistency of parameters
- Out of source builds and runs, which can be inspected or executed using the conventional
  `makenek` for debugging
- Avoid typos and human errors
- Better than bash scripting like:
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

- In development
- Requires some basic knowledge of Python to use (*not really a big issue, to
  be honest*).
- Modification of the API requires learning how
  [Snakemake](https://snakemake.readthedocs.io/en/stable/) functions and [how
  to write Jinja
  templates](https://jinja.palletsprojects.com/en/2.11.x/templates/) (which are
  not so hard, btw)

</details>

## Contributing

Contributions are welcome! You can help by testing out the code, filing issues
and submitting patches. See [contributing guidelines](CONTRIBUTING.md).
