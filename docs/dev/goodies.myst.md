# Goodies

```{note}
This document contains some useful scripts and configuration for Snek5000
development.
```

## Shell scripts

### `activate.sh`
This script can be sourced to initialize the development environment

```sh
DIR="$(pwd)"
# adds Nek5000 utilities to the PATH
export PATH="$PATH:$NEK_SOURCE_ROOT/bin"

# activate virtual environment for Nek5000
if [ -d venv ]; then
  source venv/bin/activate
elif [[ -z "$CONDA_PREFIX" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
  echo 'WARNING: no venv / conda environment present.'
  echo 'Read the docs on how to setup your Python environment: https://snek5000.readthedocs.io/en/latest/intro.html'
fi

# activate Snek5000 bash completion
if [ "$BASH_VERSION" ]; then
  if [ "$(type -P "snakemake")" ]; then
    eval "$(snakemake --bash-completion)"
  fi
fi
```

### Tarball utilities

If you use the ``archive`` Snakemake rule to generate tarball archives, then
these shell commands / functions can be of use.

```sh
function tar-help() {
  echo "tar-ls: List contents"
  echo "tar-diff: Diff 2 archives"
  echo "bsdtar xf: Extract archive"
  echo "tar -xf --wildcards 'glob_pattern': Extract using a glob pattern"
}
function tar-ls() {
  bsdtar tvf "$@"
  # tar -tvf $@ --use-compress-program=zstdmt
}
function tar-diff() {
  local argc=$#
  if [ $argc -ne 2 ]; then
    echo "Usage: tar-diff FILE1 FILE2"
    return
  fi
  diff --color=auto <(tar-ls "$1") <(tar-ls "$2")
}
```

## EditorConfig

For enforcing a uniform code-style during development, pre-commit is used, but
if your editor supports [EditorConfig](https://EditorConfig.org) then the
following configuration file can be used as `.editorconfig`.

```ini
# Unix-style newlines with a newline ending every file
[*]
indent_style = space
indent_size = 4
tab_width = 4
end_of_line = lf
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false

# Set default charset
[*.py]
charset = utf-8

# Nek5000 is full of trailing spaces
[*.f]
trim_trailing_whitespace = false

# Shell scripts, yaml, toml etc.
[*.{sh,yml,toml}]
indent_size = 2

[*.rst]
indent_size = 3

# Tab indentation (no size specified)
[{Makefile,makefile,Makefile.*}]
indent_style = tab
indent_size = unset
tab_width = unset
```

### Vim `.exrc` or `.vimrc`

if you are a Vim user the following lines in the `~/.vimrc` along with the
syntax plugin for [Snakemake in
Vim](https://github.com/snakemake/snakemake/tree/main/misc/vim) should be
useful.


```vim
"{{{ Nek5000
au BufNewFile,BufRead *.par set filetype=cfg
au BufNewFile,BufRead * if &syntax == '' | set syntax=fortran | endif
au BufNewFile,BufRead * if &filetype == '' | set ft=fortran | endif
au BufNewFile,BufRead *.usr set filetype=fortran
au BufNewFile,BufRead Snakefile set filetype=snakemake syntax=snakemake
au BufNewFile,BufRead *.smk set filetype=snakemake syntax=snakemake
"}}}

" Fuzzy search:
" Assuming Nek5000 source code is at lib/Nek5000
" Use :fin[d] command
set path=.,src/**,lib/Nek5000/core/**,tests,docs,.github/workflows
set wildignore+=*.pyc,*.o,*.so

" Ctags: https://ctags.io
" Basics
" Use :ta[g] command to search for a tag
"     CTRL-] / C-LeftMouse to go to definition
"     CTRL-T to return
set tags^=.tags

" See https://arjanvandergaag.nl/blog/navigating-project-files-with-vim.html
" Use gf in normal mode to go to a file
set suffixesadd+=.py,.f
```
