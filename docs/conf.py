# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import os
import sys
from pathlib import Path
import subprocess
from subprocess import PIPE

import breathe

sys.path.insert(0, os.fspath(Path(breathe.__file__).parent))


# -- Project information -----------------------------------------------------

project = "eturb"
copyright = "2019, Ashwin Vishnu Mohanan"
author = "Ashwin Vishnu Mohanan"

# The full version, including alpha/beta/rc tags
release = "0.0.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# Execute Doxygen
os.makedirs("_build/html/doxygen", exist_ok=True)

# Modify Doxygen configuration or not
modify_doxygen = any(
    os.getenv(env) for env in ("CI", "GITHUB_ACTIONS", "READTHEDOCS")
)
if modify_doxygen:
    print("Disabling source browser... ", end="")

    # Disable source browser
    with open("Doxyfile", "rb") as doxyfile:
        doxy_cfg = [
            line
            for line in doxyfile.readlines()
            if b"SOURCE_BROWSER" not in line
        ]
    doxy_cfg = b"".join(doxy_cfg)
    # print(doxy_cfg.decode("utf8"))


print("Executing Doxygen... ", end="")
try:
    if modify_doxygen:
        # Pass configuration via stdin
        with subprocess.Popen(
            ["doxygen", "-"], stdin=PIPE, stdout=PIPE
        ) as proc:
            doxy_output = proc.communicate(input=doxy_cfg)[0]
    else:
        doxy_output = subprocess.check_output(["doxygen"])
except FileNotFoundError:
    print(
        "Can not find doxygen to generate the documentation of the Fortran code."
    )
else:
    doxy_summary = doxy_output.decode("utf8").splitlines()[-2:]
    print("done:", *doxy_summary)

    # -- Breathe configuration ---------------------------------------------------
    extensions.append("breathe")

    # breathe_default_members = ('members', 'undoc-members')

    # File types
    breathe_implementation_filename_extensions = [".md"]
    breathe_domain_by_extension = {"usr": "f", "inc": "f"}
    breathe_domain_by_file_pattern = {"SIZE": "f"}

    # Input sources
    breathe_projects = {"eturb": "_build/xml/"}
    #  breathe_projects_source = {
    #      "abl_nek5000": ("../src/abl_nek5000", ["SIZE", "3D_ABL.usr"]),
    #  }
    breathe_default_project = "eturb"

# ----------------------------------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
