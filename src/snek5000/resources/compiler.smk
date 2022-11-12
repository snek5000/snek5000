from pprint import pprint

import snek5000
from snek5000.clusters import nproc_available
from snek5000.util import now


NEK_SOURCE_ROOT = snek5000.get_nek_source_root()


# Snakemake configuration
rule show_config:
    run:
        pprint(config)


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
    output:
        "logs/run_" + now() + ".log",
    resources:
        nproc=nproc_available(),
    params:
        redirect=">",
        end="",
    shell:
        """
        ln -sf {output} {config[CASE]}.log
        echo "Log file:"
        realpath {config[CASE]}.log
        {config[MPIEXEC]} -n {resources.nproc} {config[MPIEXEC_FLAGS]} ./nek5000 {params.redirect} {output} {params.end}
        echo $PWD
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
