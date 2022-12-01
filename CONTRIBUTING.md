# Contributing

## Installation for development

Something does not work and you wish to fix it? Are you curious to see how it works? For
development:

```sh
# First install Nek5000
git clone https://github.com/snek5000/Nek5000.git
export NEK_SOURCE_ROOT=$PWD/Nek5000

git clone https://github.com/snek5000/snek5000.git

# Activate paths: Start here. Always!
cd snek5000
source activate.sh
```

Now you should setup a Python environment. There are two ways to do this (and it has to
be done only once):

- Using `venv`

  ```sh
  python -m venv venv
  source venv/bin/activate
  ```

- Using `conda`

  ```sh
  conda env create -n env-snek5000
  conda activate env-snek5000
  ```

Finally, to install in development mode:

```sh
pip install pip-tools nox
nox -s pip-sync
```

## General guidelines

- **Editor**: Use an editor which supports [EditorConfig](http://editorconfig.org/)

- **Style guide**: For Python code, `black`, `isort` and `flake8` are used to check and
  lint. Installing `pre-commit` would enforce the style automatically as a git hook.

  ```sh
  pre-commit install
  ```

- **Branching model**: The development uses branches and pull-requests for experimental
  features. You may find the following git branches when you clone `snek5000`:

  - `master`: main branch
  - `fix/...`, `enh/...`: feature branches

  Executing the following command would configure git to work with submodules easily and
  ensures consistency:

- **Testing**: [Run `pytest`](https://pytest.readthedocs.io/) from the top-level
  directory. The test-cases can be found under `tests/` directory. To run the slow tests
  too execute `pytest --runslow`.

- **Debugging**: Set the environment variable:

  ```bash
  export SNEK_DEBUG=true
  ```

  to activate debugging logs and longer tests.

## Vim

Vim users could benefit by setting:

```vim
set secure exrc
```

This sources the `.exrc` file which comes along with the repository and enables syntax
highlighting for file extensions used in `Nek5000`.
