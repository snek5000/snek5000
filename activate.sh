DIR="$(pwd)"
export SOURCE_ROOT="$DIR/lib/Nek5000"
export PATH="$PATH:$SOURCE_ROOT/bin"

alias smake="snakemake"

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
