# eturb
Efficient simulations of turbulent atmospheric boundary layer.

## Getting started

```sh
# Clone
git clone --recursive git@github.com:exabl/eturb.git

# Activate paths: Start here. Always!
cd eturb
source activate.sh

# Build Nek5000
cd lib/Nek5000/tools/
./maketools all
cd -

```

## Workflow

### Easy way

```sh
# Setup python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # only once


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

```

### Hard way

```sh
# Build case
cd src/abl_nek5000/
CASE="3D_ABL"
echo "$CASE.box" | genbox
mv -f box.re2 3D_ABL.re2
echo "$CASE\n0.01" | genmap
FFLAGS="-mcmodel=medium -march=native" CFLAGS="-mcmodel=medium -march=native" makenek
cd -

# Run case
cd src/abl_nek5000/
nekmpi $CASE <nb_procs> # foreground
nekbmpi $CASE <nb_procs> # background
cd -


# Clean
makenek clean

```

## Development

See [contributing guidelines](CONTRIBUTING.md).
