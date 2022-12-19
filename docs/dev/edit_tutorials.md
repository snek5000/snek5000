# How to work on tutorials

The tutorials are saved and version controlled as `.myst.md` files (md:myst format) in
the `docs` directory. They can be opened as standard text file with your favorite text
editor. Moreover, these files can be opened as notebooks in Jupyter Lab. One needs to
start Jupyter Lab from the `docs` directory. When [Jupytext] is installed, you should be
able to click right on the icon corresponding to the file and to choose "Open with ->
Notebook". Saving the notebook in the Jupyter interface should also saved the MyST file!

Note that some files are coupled with a Python script in `docs/examples/scripts`.

```{warning}
One has to delete the `.ipynb` files before building the whole documentation with Sphinx.
```

[jupytext]: https://jupytext.readthedocs.io
