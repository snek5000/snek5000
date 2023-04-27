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
import runpy
import subprocess
import sys
from datetime import date
from pathlib import Path
from subprocess import PIPE

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata

import breathe

import snek5000
from snek5000 import util
from snek5000.config import ensure_config_file

ensure_config_file()


def root(module):
    return os.fspath(Path(module.__file__).parent)


sys.path.insert(0, root(breathe))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, root(snek5000))

NEK_SOURCE_ROOT = snek5000.get_nek_source_root()
print("NEK_SOURCE_ROOT = ", NEK_SOURCE_ROOT)
print("sys.path =\n   ", "\n    ".join(sys.path))

# -- Project information -----------------------------------------------------

project = "snek5000"
_meta = metadata.metadata(project)
_today = date.today()
copyright = (
    f"2019 - {_today.year}, Ashwin Vishnu Mohanan. Published: {_today.isoformat()}"
)
author = "Ashwin Vishnu Mohanan"

version = ".".join(snek5000.__version__.split(".")[:3])
# The full version, including alpha/beta/rc tags
release = snek5000.__version__

_py_min_version = _meta.get("Requires-Python").split(">=")[-1]

rst_prolog = f"""
.. |author| replace:: {author}
.. |today| replace:: {_today}
.. |py_min_version| replace:: {_py_min_version}
"""

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_inline_tabs",
    "IPython.sphinxext.ipython_console_highlighting",
    # "recommonmark",
    # "myst_parser",
    "myst_nb",
    "sphinx_copybutton",
]

# Execute ipynb files into with a cache ...
nb_execution_mode = "cache"
# ... except these ipynb files
nb_execution_excludepatterns = ["**/*.ipynb", "debug/**/*"]
nb_execution_raise_on_error = True
nb_execution_show_tb = True
nb_execution_timeout = 600
nb_merge_streams = True

# CSS selector which modifies the sphinx-copybutton feature
copybutton_selector = ",".join(
    [
        f"div.highlight-{css_class} div.highlight pre"
        for css_class in ("python", "ipython3", "sh", "ini", "default")
    ]
)

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".myst.md": "myst-nb",
}

# Execute Doxygen
os.makedirs("_build/html/doxygen", exist_ok=True)

# Inspect whether to run doxygen or not
last_modified = util.last_modified(NEK_SOURCE_ROOT).stat().st_mtime
timestamp = Path("_build/.doxygen_timestamp")
if timestamp.exists() and Path("_build/xml").exists():
    with open(timestamp) as fp:
        last_documented = float(fp.read())
    exec_doxygen = last_documented < last_modified
else:
    exec_doxygen = True

# Modify Doxygen configuration or not
#  modify_doxygen = any(os.getenv(env) for env in ("CI", "GITHUB_ACTIONS", "READTHEDOCS"))
modify_doxygen = False
if modify_doxygen:
    print("Disabling source browser... ", end="")

    # Disable source browser
    with open("Doxyfile", "rb") as doxyfile:
        doxy_cfg = [
            line for line in doxyfile.readlines() if b"SOURCE_BROWSER" not in line
        ]
    doxy_cfg = b"".join(doxy_cfg)
    # print(doxy_cfg.decode("utf8"))


try:
    if exec_doxygen:
        print("Executing Doxygen... ", end="")
        if modify_doxygen:
            # Pass configuration via stdin
            with subprocess.Popen(["doxygen", "-"], stdin=PIPE, stdout=PIPE) as proc:
                doxy_output = proc.communicate(input=doxy_cfg)[0]
        else:
            doxy_output = subprocess.check_output(["doxygen"])

        doxy_summary = doxy_output.decode("utf8").splitlines()[-2:]
        print("done:", *doxy_summary)
        with open(timestamp, "w") as fp:
            fp.write(str(last_modified))
    else:
        print(
            f"Using old Doxygen XML output... Remove {timestamp} to force doxygen build."
        )
except FileNotFoundError:
    print("Can not find doxygen to generate the documentation of the Fortran code.")
else:
    # -- Breathe configuration ---------------------------------------------------
    extensions.append("breathe")

    # File types
    breathe_implementation_filename_extensions = [".md"]
    breathe_domain_by_extension = {"usr": "fortran", "f": "fortran"}
    breathe_domain_by_file_pattern = {"SIZE": "f"}

    # Input sources
    breathe_projects = {"snek5000": "_build/xml/"}
    breathe_default_project = "snek5000"

# ----------------------------------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
#  source_suffix = [".rst", ".md"]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "examples/snek5000-*/README.md",
    "joss_paper/paper.md",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"


# Set link name generated in the top bar.
html_title = ""

html_theme_options = {
    k: v
    for k, v in runpy.run_path("html_theme_options.py").items()
    if not k.startswith("__")
}
#  html_sidebars = {
#      "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
#  }

html_favicon = "_static/favicon.ico"
html_logo = "_static/icon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# Values to pass into the template engine's context for all pages.
html_context = {
    "sidebar_external_links_caption": "Links",
    "sidebar_external_links": [
        (
            '<i class="fa fa-cube fa-fw"></i> PyPI',
            f"https://pypi.org/project/{project.lower()}",
        ),
        #  (
        #      '<i class="fa fa-cube fa-fw"></i> Conda forge',
        #      f"https://anaconda.org/conda-forge/{project.lower()}",
        #  ),
        (
            '<i class="fa fa-code fa-fw"></i> Source code',
            f"https://github.com/snek5000/{project.lower()}",
        ),
        (
            '<i class="fa fa-bug fa-fw"></i> Issue tracker',
            f"https://github.com/snek5000/{project.lower()}/issues",
        ),
        #  ('<i class="fa fa-rss fa-fw"></i> Blog', 'https://...'),
        #  (
        #      '<i class="fa fa-comments fa-fw"></i> Chat',
        #      "https://matrix.to/#/#snek5000:matrix.org",
        #  ),
        #  (
        #      '<i class="fa fa-file-text fa-fw"></i> Citation',
        #      "https://doi.org/10.5334/jors.237",
        #  ),
    ],
}
# -- Options for Intersphinx -------------------------------------------------
intersphinx_mapping = runpy.run_path("ls_intersphinx_targets.py")["intersphinx_mapping"]

# -- Other options ------------------------------------------------------------
autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    #  'special-members': '__init__',
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "inherited-members": True,
}
autodoc_mock_imports = ["IPython"]

todo_include_todos = True

napoleon_numpy_docstring = True

# -- Custom functions --------------------------------------------------------


def autodoc_skip_member(app, what, name, obj, skip, options):
    # return True if (skip or exclude) else None
    # Can interfere with subsequent skip functions.
    if what == "function" and name == "load" and obj is snek5000.load:
        return True


def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member)


myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3
