# Project *eTurb*

[![](https://github.com/exabl/snek5000/workflows/Tests/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Tests)
[![](https://github.com/exabl/snek5000/workflows/Docs/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Docs)

**Efficient** simulations of **turbulent** atmospheric boundary layer.


## Installation

```sh
# Clone
git clone --recursive git@github.com:exabl/snek5000.git

# Activate paths: Start here. Always!
cd snek5000
source activate.sh

# Build Nek5000
cd lib/Nek5000/tools/
./maketools all
cd -

```

## Workflow

### Easy way

This workflow requires you to setup a Python environment. There are two ways to
do this (and it has to be done only once):

-  Using `venv`
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```
-  Using `conda`
   ```sh
   conda env create -n snek5000 -f environment.yml
   conda activate snek5000
   pip install -e .
   ```
After setting up Python, you can do either of the following:

1. Run **Snakemake** in a bash (or similar) console:
   ```sh
   # Everything done via a Snakefile at once
   cd src/abl_nek5000/
   snakemake run
   cd -

   # ... or one by one
   cd src/abl_nek5000/
   snakemake mesh
   snakemake compile
   snakemake run
   snakemake archive
   snakemake clean
   cd -

2. Use the **[`snek5000` Python
   API](https://exabl.github.io/snek5000/_generated/snek5000.html)**, based on
   [fluidsim](https://fluidsim.readthedocs.io)
   ```python
   from snek5000.solvers.abl import Simul

   params = Simul.create_default_params()

   # modify parameters as needed

   sim = Simul(params)
   sim.make.exec()  # by default starts a run
   sim.make.exec(["mesh", "compile"])  # run rules in order
   sim.make.exec(["run"], dryrun=True)  # simulate
   ```

### Hard way

```sh
# Build case
cd src/abl/
CASE="abl"
echo "$CASE.box" | genbox
mv -f box.re2 abl.re2
echo "$CASE\n0.01" | genmap
FFLAGS="-mcmodel=medium -march=native" CFLAGS="-mcmodel=medium -march=native" makenek
cd -

# Run case
cd src/abl/
nekmpi $CASE <nb_procs> # foreground
nekbmpi $CASE <nb_procs> # background
cd -


# Clean
makenek clean

```

## Development

See [contributing guidelines](CONTRIBUTING.md).
