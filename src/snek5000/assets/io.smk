import itertools
from glob import iglob

import snek5000
from snek5000.util.archive import tar_name, archive, clean_simul


NEK_SOURCE_ROOT = snek5000.source_root()


# clean compiler output
rule clean:
    shell:
        """
        echo "cleaning Nek5000 ..."
        rm -fv {config[CASE]}.f nek5000
        rm -rf obj
        rm -fv $NEK_SOURCE_ROOT/core/mpif.h
        """


# clean simulation files
rule cleansimul:
    params:
        tarball=tar_name(compress_format=".zst"),
    run:
        clean_simul(config["CASE"], params.tarball)


# clean third party
rule clean3rd:
    params:
        gslib_dir=NEK_SOURCE_ROOT + "/3rd_party/gslib",
    shell:
        """
        nekconfig clean < <(yes)
        rm -rf {params.gslib_dir}/{{gslib-*,*.tar.gz}}
        """


# clean everything
rule cleanall:
    shell:
        """
        rm -rf obj
        snakemake clean clean3rd cleansimul -j
        """


# create an archive with all the results
rule archive:
    params:
        solution=sorted(
            itertools.chain.from_iterable(
                (
                    iglob(f"{prefix}{config['CASE']}0.f*")
                    for prefix in ("", "c2D", "sts")
                )
            )
        ),
        rest=[
            "SESSION.NAME",
            "params_simul.xml",
            "SIZE",
            *iglob(f"rs6{config['CASE']}0.f*"),
            f"{config['CASE']}.re2",
            f"{config['CASE']}.ma2",
            f"{config['CASE']}.par",
            f"{config['CASE']}.usr",
        ],
        tarball=tar_name(),
    run:
        archive(params.tarball, params.solution, remove=True)
        archive(params.tarball, params.rest)
        archive(params.tarball + ".zst", readonly=True)
