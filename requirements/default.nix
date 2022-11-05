# Use `nix-shell --pure` to verify if the conda/mamba/micromamba spec in
# environment.yaml is sufficient or not
{ pkgs ? import <nixpkgs> {} }:

let
  fhs = pkgs.buildFHSUserEnv {
    name = "snek5000-conda-nix-dev";

    targetPkgs = _: [
      pkgs.micromamba
    ];

    profile = ''
      set -e
      eval "$(micromamba shell hook -s bash)"
      export MAMBA_ROOT_PREFIX=${builtins.getEnv "PWD"}/.mamba
      pushd ..
      micromamba create --quiet --name snek -c conda-forge pip pypy
      micromamba activate snek
      micromamba install --yes --file requirements/environment.yaml
      python -m pip install -r requirements/dev.txt
      popd
      set +e
    '';
  };
in fhs.env
