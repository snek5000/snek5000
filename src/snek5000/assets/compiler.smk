from pprint import pprint

import snek5000
from snek5000.clusters import nproc_available
from snek5000.util import now


NEK_SOURCE_ROOT = snek5000.source_root()


# Snakemake configuration
rule show_config:
    run:
        pprint(config)


# gslib, lapack ...
rule build_third_party:
    input:
        # ".state",
        config["file"],
        nekconfig=NEK_SOURCE_ROOT + "/bin/nekconfig",
    output:
        NEK_SOURCE_ROOT + "/3rd_party/gslib/lib/libgs.a",
        NEK_SOURCE_ROOT + "/3rd_party/blasLapack/libblasLapack.a",
    shell:
        """
        export CC="{config[MPICC]}" FC="{config[MPIFC]}" \
            CFLAGS="{config[CFLAGS]}" FFLAGS="{config[FFLAGS]}"
        {input.nekconfig} -build-dep
        """


# compile
rule compile:
    input:
        "SIZE",
        f"{config['CASE']}.usr",
        "makefile_usr.inc",
        "makefile",
        NEK_SOURCE_ROOT + "/3rd_party/gslib/lib/libgs.a",
        NEK_SOURCE_ROOT + "/3rd_party/blasLapack/libblasLapack.a",
    params:
        make="make",
    output:
        exe="nek5000",
    shell:
        """
        {params.make} -j {output.exe} | tee -a build.log
        """


# mpiexec
rule mpiexec:
    input:
        f"{config['CASE']}.re2",
        f"{config['CASE']}.ma2",
        f"{config['CASE']}.par",
        "SESSION.NAME",
        "nek5000",
    log:
        "logs/run_" + now() + ".log",
    resources:
        nproc=nproc_available(),
    params:
        redirect=">",
        end="",
    shell:
        """
        ln -sf {log} {config[CASE]}.log
        echo "Log file:"
        realpath {config[CASE]}.log
        {config[MPIEXEC]} -n {resources.nproc} ./nek5000 {params.redirect} {log} {params.end}
        """


# run in background
use rule mpiexec as run with:
    params:
        redirect=">",
        end="&",


# run in foreground
use rule mpiexec as run_fg with:
    params:
        redirect="| tee",
        end="",
