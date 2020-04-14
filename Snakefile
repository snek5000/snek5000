rule env_export:
    shell:
        """
        conda env export -f environment.yml
        sed -i '/^prefix/d' environment.yml
        """

rule env_update:
    shell: 'conda env update --file environment.yml'

rule requirements:
    input: 'requirements.in'
    output: 'requirements.txt'
    shell: 'pip-compile'

rule develop:
    shell: 'pip install -e .[dev]'

rule docs:
    input: 'src/'
    shell: 'cd docs && SPHINXOPTS="-W" make html'

rule docs_clean:
    shell: 'cd docs && SPHINXOPTS="-W" make cleanall'

rule ctags:
    input:
        nek5000='lib/Nek5000/core',
        abl='src/abl',
        eturb='src/eturb'
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
        ctags -f {output} {params.excludes} --append -R {input.eturb}
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
