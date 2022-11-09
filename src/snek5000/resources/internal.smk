import snek5000
from snek5000.util.files import create_session


NEK_SOURCE_ROOT = snek5000.get_nek_source_root()


# generate a box mesh
rule generate_box:
    input:
        box=f"{config['CASE']}.box",
        genbox=NEK_SOURCE_ROOT + "/bin/genbox",
    output:
        "box.re2",
    shell:
        "{input.genbox} <<< {input.box}"


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
        genmap=NEK_SOURCE_ROOT + "/bin/genmap",
    output:
        f"{config['CASE']}.ma2",
    resources:
        tolerance="0.01",
    shell:
        r'printf "{config[CASE]}\n{resources.tolerance}\n" '
        "  | {input.genmap} "
        "  | (head -n 20; tail -n 10) "


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
    input:
        re2=f"{config['CASE']}.re2",
        ma2=f"{config['CASE']}.ma2",
        par=f"{config['CASE']}.par",
    output:
        "SESSION.NAME",
    run:
        create_session(config["CASE"], input.re2, input.ma2, input.par)
