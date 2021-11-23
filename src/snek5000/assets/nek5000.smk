MAKETOOLS = f"CC={config['CC']} FC={config['FC']} CFLAGS='{config['CFLAGS']}' FFLAGS='{config['FFLAGS']}' ./maketools"


rule tools:
    params:
        maketools=MAKETOOLS,
    shell:
        """
        pushd tools/
        {params.maketools} all
        """


rule _tool:
    input:
        "tools/{tool}",
    output:
        "bin/{tool}",
    params:
        maketools=MAKETOOLS,
    shell:
        """
        pushd tools/
        {params.maketools} {wildcards.tool}
        """


rule tools_clean:
    shell:
        """
        rm -rf 3rd_party/gslib/lib 3rd_party/gslib/gslib
        pushd tools/
        ./maketools clean
        """


# NOTE: May not compile as needed unless proper flags are supplied. The command
# makenek takes care of gslib building using the bash function make_3rd_party
rule build_third_party:
    input:
        nekconfig="bin/nekconfig",
    output:
        "3rd_party/gslib/lib/libgs.a",
        "3rd_party/blasLapack/libblasLapack.a",
    shell:
        """
        export CC="{config[MPICC]}" FC="{config[MPIFC]}" \
            CFLAGS="{config[CFLAGS]}" FFLAGS="{config[FFLAGS]}"
        {input.nekconfig} -build-dep
        """
