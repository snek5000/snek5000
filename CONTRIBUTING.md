# Developer guide

## General guidelines


* **Editor**: Use an editor which supports [EditorConfig](http://editorconfig.org/)
* **Style guide**: Follow [Fortran best practices](https://www.fortran90.org/src/best-practices.html)
* **Branching model**: The development uses branches and pull-requests for experimental features. We
  also rely on [git submodules](https://www.git-scm.com/docs/git-submodule) to
  track other libraries. The following branches are important:

  * `eturb`:
    * `master`: main branch
    * `develop`: development branch
  * `lib/Nek5000`:
    * `master`: upstream branch
    * `stable`: main branch tracking the stable version 17
    * `develop`: development branch

## Vim

Vim users could benefit by setting:
```vim
set exrc
set secure
```
which enables syntax highlighting for file extensions used in `lib/Nek5000`.
