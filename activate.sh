DIR="$(pwd)"
export NEK_SOURCE_ROOT="$DIR/lib/Nek5000"
export PATH="$PATH:$NEK_SOURCE_ROOT/bin"
export FLUIDSIM_TRANSONIC_BACKEND=python

alias smake="snakemake"
# tarball utilities
function tar-help() {
  echo "tar-ls: List contents"
  echo "tar-diff: Diff 2 archives"
  echo "bsdtar xf: Extract archive"
  echo "tar -xf --wildcards 'glob_pattern': Extract using a glob pattern"
}
function tar-ls() {
  bsdtar tvf $@
  # tar -tvf $@ --use-compress-program=zstdmt
}
function tar-diff() {
  local argc=$#
  if [ $argc -ne 2 ]; then
    echo "Usage: tar-diff FILE1 FILE2"
    return
  fi
  diff --color=auto <(tar-ls $1) <(tar-ls $2)
}

if [ -d venv ]; then
  source venv/bin/activate
elif [[ -z "$CONDA_PREFIX" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
  echo 'WARNING: no venv / conda environment present.'
  echo 'Read the docs on how to setup your Python environment: https://exabl.github.io/snek5000/README.html#installation'
fi

if [ "$BASH_VERSION" ]; then
  if [ $(type -P "snakemake") ]; then
    eval $(snakemake --bash-completion)
  fi
fi
