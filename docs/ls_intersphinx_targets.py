import sys

# NOTE: If intersphinx_mapping is updated, add the keys to the Makefile
# variable INTERSPHINX_TARGETS

intersphinx_mapping = dict(
    python=("https://docs.python.org/3", None),
    nek=("https://nek5000.github.io/NekDoc", None),
    jinja2=("https://jinja.palletsprojects.com/en/3.0.x", None),
    fluiddyn=("https://fluiddyn.readthedocs.io/en/latest", None),
    fluidsim=("https://fluidsim.readthedocs.io/en/latest", None),
    pymech=("https://pymech.readthedocs.io/en/latest", None),
)


if __name__ == "__main__":
    try:
        url = "/".join((intersphinx_mapping[sys.argv[1]][0], "objects.inv"))
    except (KeyError, IndexError):
        print(
            f"""
usage: {sys.argv[0]} [PROJECT]

POSITIONAL ARGUMENTS
  project \t one of the following {intersphinx_mapping.keys()}
    """
        )
        raise

    from sphinx.ext.intersphinx import inspect_main

    inspect_main([url])
