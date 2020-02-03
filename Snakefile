rule environment:
    shell:
        """
        conda env export -f environment.yml
        sed -i '/^prefix/d' environment.yml
        """

rule requirements:
    input: 'requirements.in'
    output: 'requirements.txt'
    shell: 'pip-compile'

rule develop:
    shell: 'pip install -e .[dev]'

rule docs:
    input: 'src/'
    shell: 'cd docs && SPHINXOPTS="-W" make html'

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

rule salloc:
    params:
        project='snic2019-1-2',
        walltime='05:00'
    shell:
        'interactive -A {params.project} -t {params.walltime} -N 1'
