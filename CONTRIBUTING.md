# Contributing

## Installation for development

Something does not work and you wish to fix it? Are you curious to see how it works? For
development:

```sh
# First install Nek5000
git clone https://github.com/snek5000/Nek5000.git
export NEK_SOURCE_ROOT=$PWD/Nek5000

git clone https://github.com/snek5000/snek5000.git
cd snek5000
```

Now you should setup a Python environment. Here, we show how to do it with the package
`venv`:

```sh
python -m venv venv
source venv/bin/activate
```

Finally, to install in development mode:

```sh
pip install pip-tools nox
nox -s sync
```

````{note}
From the root directory of the project, one can then activate the dev
environment with:
```sh
source activate.sh
```
````

## General guidelines

- **Style guide**: For Python code, `black`, `isort` and `flake8` are used to check and
  lint. Installing `pre-commit` would enforce the style automatically as a Git hook.

  ```sh
  pre-commit install
  ```

- **Branching model**: The development uses branches and pull-requests for experimental
  features. You may find the following Git branches when you clone `snek5000`:

  - `main`: main branch
  - `fix/...`, `enh/...`: feature branches

- **Testing**: [Run `pytest`](https://pytest.readthedocs.io/) from the top-level
  directory. The test-cases can be found under `tests/` directory. To run the slow tests
  too execute `pytest --runslow`.

- **Debugging**: Set the environment variable:

  ```sh
  export SNEK_DEBUG=true
  ```

  to activate debugging logs and longer tests.

See also our [](./dev/index.rst).

## Goodies

See [here](./dev/goodies).
