from pprint import pprint

import snek5000
from snek5000.util import now


NEK_SOURCE_ROOT = snek5000.source_root()


# Snakemake configuration
rule show_config:
    run:
        pprint(config)


# gslib, lapack ...
rule build_third_party:
    input:
        ".state",
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
        f"{config['CASE']}.f",
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
    params:
        nproc=str(os.cpu_count()),
        redirect=">",
        end="",
    shell:
        """
        ln -sf {log} {config[CASE]}.log
        echo "Log file:"
        realpath {config[CASE]}.log
        {config[MPIEXEC]} -n {params.nproc} ./nek5000 {params.redirect} {log} {params.end}
        """


# run in background
use rule mpiexec as run with:
    params:
        nproc=str(os.cpu_count()),
        redirect=">",
        end="&",


# run in foreground
use rule mpiexec as srun with:
    params:
        nproc=str(os.cpu_count()),
        redirect="| tee",
        end="",
