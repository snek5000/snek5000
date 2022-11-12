"""Console script functions

"""

from snek5000.solvers import available_solvers


def print_versions():

    import snakemake
    import pymech
    import fluidsim_core
    import fluiddyn
    import snek5000

    versions = {"Package": "Version", "-------": "-------"}

    packages = [snek5000, fluiddyn, fluidsim_core, pymech, snakemake]
    for package in packages:
        versions[package.__name__] = package.__version__

    for pkg_name, version in versions.items():
        print(f"{pkg_name.ljust(15)} {version}")

    names = sorted(set([entry_point.name for entry_point in available_solvers()]))
    print("\nInstalled solvers: " + ", ".join(names))
