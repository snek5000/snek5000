DIR="$(pwd)"
export SOURCE_ROOT="$DIR/lib/Nek5000"
export PATH="$PATH:$SOURCE_ROOT/bin"
if [ -d venv ]; then
  source venv/bin/activate
else
  echo WARNING: no venv present. Try running 'python -m venv venv'
fi
