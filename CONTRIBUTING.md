# Contributing

## Installation for development

Something does not work and you wish to fix it? Are you curious to see how it
works? For development:
```sh
# Clone
git clone --recursive https://github.com/exabl/snek5000.git

# Activate paths: Start here. Always!
cd snek5000
source activate.sh
```

Now you should setup a Python environment. There are two ways to
do this (and it has to be done only once):

-  Using `venv`
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
-  Using `conda`
   ```sh
   conda env create -n snek5000
   conda activate snek5000
   ```

Finally, to install in development mode:
```sh
pip install -e '.[dev]'
pip install "phill @ git+https://github.com/exabl/snek5000-phill.git"
```

## General guidelines

* **Editor**: Use an editor which supports [EditorConfig](http://editorconfig.org/)
* **Style guide**: For Python code, `black`, `isort` and `flake8` are used to
  check and lint. Installing `pre-commit` would enforce the style automatically
  as a git hook.

  ```sh
  pre-commit install
  ```

* **Branching model**: The development uses branches and pull-requests for experimental features. We
  also rely on [git submodules](https://www.git-scm.com/docs/git-submodule) to
  track `Nek5000`. You may find the following git branches when you clone
  `snek5000`:

    * `master`: main branch
    * `fix/...`, `enh/...`: feature branches

  Executing the following command would configure git to work with submodules
  easily and ensures consistency:
  ```sh
  # Enable recursion for relevant commands, such that
  # regular commands recurse into submodules by default
  git config submodule.recurse true
  ```

* **Testing**: [Run `pytest`](https://pytest.readthedocs.io/) from the
  top-level directory. The test-cases can be found under `tests/` directory.
* **Debugging**: Set the environment variable:
  ```bash
  export SNEK_DEBUG=true
  ```
  to activate debugging logs and longer tests.

## Vim

Vim users could benefit by setting:
```vim
set secure exrc
```
This sources the `.exrc` file which comes along with the repository and
enables syntax highlighting for file extensions used in `lib/Nek5000`.
