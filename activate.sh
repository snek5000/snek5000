DIR="$(pwd)"
export SOURCE_ROOT="$DIR/lib/Nek5000"
export PATH="$PATH:$SOURCE_ROOT/bin"

alias smake="snakemake"
# tarball utilities
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
elif [ -z "$CONDA_PREFIX" ]; then
  echo 'WARNING: no venv / conda environment present.'
  echo 'Read the docs on how to setup your Python environment: https://exabl.github.io/eturb/README.html#easy-way'
fi

if [ "$BASH_VERSION" ]; then
  if [ $(type -P "snakemake") ]; then
    eval $(snakemake --bash-completion)
  fi
fi
