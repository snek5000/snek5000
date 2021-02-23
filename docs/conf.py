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
import subprocess
import sys
from datetime import date
from pathlib import Path
from subprocess import PIPE

import breathe
import snek5000
from snek5000 import util


def root(module):
    return os.fspath(Path(module.__file__).parent)


sys.path.insert(0, root(breathe))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, root(snek5000))

print("sys.path =\n   ", "\n    ".join(sys.path))

# -- Project information -----------------------------------------------------

project = "snek5000"
_today = date.today()
copyright = (
    f"2019 - {_today.year}, Ashwin Vishnu Mohanan. Published: {_today.isoformat()}"
)
author = "Ashwin Vishnu Mohanan"

version = ".".join(snek5000.__version__.split(".")[:3])
# The full version, including alpha/beta/rc tags
release = snek5000.__version__


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
    #  "recommonmark",
    #  "myst_parser",
    "myst_nb",
    "sphinx_copybutton",
]

# Execute ipynb files into with a cache ...
jupyter_execute_notebooks = "cache"
# ... except these ipynb files
execution_excludepatterns = ["ipynb/executed/*"]

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
    ".myst": "myst-nb",
}

# Execute Doxygen
os.makedirs("_build/html/doxygen", exist_ok=True)

# Inspect whether to run doxygen or not
last_modified = util.last_modified("../lib").stat().st_mtime
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

    # breathe_default_members = ('members', 'undoc-members')

    # File types
    breathe_implementation_filename_extensions = [".md"]
    breathe_domain_by_extension = {"usr": "fortran", "f": "fortran"}
    breathe_domain_by_file_pattern = {"SIZE": "f"}

    # Input sources
    breathe_projects = {"snek5000": "_build/xml/"}
    #  breathe_projects_source = {
    #      "abl": ("../src/abl", ["SIZE", "abl.usr"]),
    #  }
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
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_material"


# Set link name generated in the top bar.
html_title = "main docs"

html_sidebars = {
    "*[!index]": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

html_favicon = "_static/favicon.ico"

# Material theme options (see theme.conf for more information)
html_theme_options = {
    # Set the name of the project to appear in the navigation.
    "nav_title": f"{project} documentation",
    # ??
    "touch_icon": html_favicon,
    # Logo to the left of the title
    "logo_icon": "&#x1F30A",  # https://emojipedia.org/water-wave/
    #
    "nav_links": [{"href": "doxygen/index", "title": "fortran docs", "internal": True}],
    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    "base_url": f"https://{project}.readthedocs.io",
    # Set the color and the accent color
    "color_primary": "indigo",
    "color_accent": "deep-purple",
    # Set the repo location to get a badge with stats
    "repo_url": f"https://github.com/exabl/{project}/",
    "repo_name": project,
    # Visible levels of the global TOC; -1 means unlimited
    "globaltoc_depth": 1,
    # If False, expand all TOC entries
    "globaltoc_collapse": True,
    # If True, show hidden TOC entries
    "globaltoc_includehidden": False,
}

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
            f"https://github.com/exabl/{project.lower()}",
        ),
        (
            '<i class="fa fa-bug fa-fw"></i> Issue tracker',
            f"https://github.com/exabl/{project.lower()}/issues",
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

intersphinx_mapping = dict(
    python=("https://docs.python.org/3", None),
    nek=("https://nek5000.github.io/NekDoc", None),
    jinja2=("https://jinja.palletsprojects.com/en/2.10.x", None),
)

# -- Other options ------------------------------------------------------------
autosummary_generate = True

autodoc_default_options = {
    "members": True,
    #  'member-order': 'bysource',
    #  'special-members': '__init__',
    #  'undoc-members': True,
    #  'exclude-members': '__weakref__'
}
autodoc_mock_imports = ["IPython"]

todo_include_todos = True

napoleon_numpy_docstring = True
