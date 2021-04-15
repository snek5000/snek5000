import snek5000


NEK_SOURCE_ROOT = snek5000.source_root()


subworkflow Nek5000:
    workdir:
        NEK_SOURCE_ROOT
    snakefile:
        snek5000.get_asset("nek5000.smk")
    configfile:
        config["file"]


# generate a box mesh
rule generate_box:
    input:
        box=f"{config['CASE']}.box",
        genbox=Nek5000("bin/genbox"),
    output:
        "box.re2",
    shell:
        "echo {input.box} | "
        "{input.genbox}"


# rename mesh file re2
rule move_box:
    input:
        "box.re2",
    output:
        f"{config['CASE']}.re2",
    shell:
        "mv -f {input} {output}"


# generate map / connectivity matrix
rule generate_map:
    input:
        f"{config['CASE']}.re2",
        genmap=Nek5000("bin/genmap"),
    output:
        f"{config['CASE']}.ma2",
    params:
        tolerance=0.01,
    shell:
        'echo "{config[CASE]}\n{params.tolerance}" | '
        "{input.genmap}"


# generate makefile
rule generate_makefile:
    input:
        f"{config['CASE']}.re2",
        f"{config['CASE']}.ma2",
        f"{config['CASE']}.usr",
        cmd=NEK_SOURCE_ROOT + "/bin/nekconfig",
    output:
        "makefile",
        ".state",
    shell:
        """
        set +u  # Do not error on undefined bash variables
        export CC="{config[MPICC]}" FC="{config[MPIFC]}" \
            CFLAGS="{config[CFLAGS]}" FFLAGS="{config[FFLAGS]} {config[includes]}" \
            USR="{config[objects]}"
        {input.cmd} {config[CASE]}
        """


# generate sessionfile
rule generate_session:
    output:
        "SESSION.NAME",
    shell:
        """
        touch SESSION.NAME
        echo {config[CASE]} > SESSION.NAME
        echo `pwd`'/' >>  SESSION.NAME
        """
