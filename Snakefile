from glob import iglob
from snek5000.util.archive import tar_name, archive

PYTHON_DIRECTORIES = ["docs", "src", "tests"]


rule env_export:
    shell:
        """
        conda env export -f environment.yml
        sed -i '/^prefix/d' environment.yml
        sed -i '/snek5000/d' environment.yml
        """

rule env_update:
    shell: 'conda env update --file environment.yml'

rule develop:
    shell: 'pip install -e .[dev]'

rule docs:
    input: 'src/'
    shell: 'cd docs && SPHINXOPTS="-W" make html'

rule docs_clean:
    shell: 'cd docs && SPHINXOPTS="-W" make cleanall'

rule bin_archive:
    input:
        iglob('bin/SLURM*'),
        iglob('bin/launcher_20*')
    output:
        tar_name(
            Path.cwd(), "bin/SLURM*", subdir="bin",
            default_prefix="archive"
        )
    run:
        archive(output, input, remove=True)


rule ctags:
    input:
        nek5000='lib/Nek5000/core',
        abl='src/abl',
        snek5000='src/snek5000'
    output:
        '.tags'
    params:
        excludes = ' '.join(
            (
                f'--exclude={pattern}'
                for pattern in
                (
                    '.snakemake',
                    '__pycache__',
                    'obj',
                    'logs',
                    '*.tar.gz',
                    '*.f?????'
                )
            )
        )
    shell:
        """
        ctags -f {output} --language-force=Fortran -R {input.nek5000}
        ctags -f {output} {params.excludes} --append --language-force=Fortran -R {input.abl}
        ctags -f {output} {params.excludes} --append -R {input.snek5000}
        """

rule watch:
    params:
        per_second=5,
        rules='docs ctags'
    shell:
        'nohup watch -n {params.per_second} snakemake {params.rules} 2>&1 > /tmp/watch.log&'

rule squeue:
    params:
        per_second=59,
        rules='docs ctags'
    shell:
        'watch -n {params.per_second} squeue -u $USER --start'

rule salloc:
    params:
        # project='snic2019-1-2',
        # walltime='05:00',
        project='snic2014-10-3 --reservation=dcs',
        walltime='30:00',
        nproc=8
    shell:
        'interactive -A {params.project} -t {params.walltime} -n {params.nproc}'

rule ipykernel:
    shell: 'ipython kernel install --user --name=$(basename $CONDA_PREFIX)'

rule jlab:
    shell:
        """
        echo '-----------------------------------------'
        echo '        Setup an SSH tunnel to           '
        printf '        '
        hostname
        echo '-----------------------------------------'
        jupyter-lab --no-browser --port=5656
        """

rule lint:
    input: PYTHON_DIRECTORIES
    shell: "black --check {input}"

rule fix:
    input: PYTHON_DIRECTORIES
    shell: 'black {input}'
