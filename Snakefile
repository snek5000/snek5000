from glob import iglob
from snek5000.util.archive import tar_name, archive


rule env_export:
    shell:
        """
        conda env export -f environment.yml
        sed -i '/^prefix/d' environment.yml
        sed -i '/snek5000/d' environment.yml
        """


rule env_update:
    shell:
        "conda env update --file environment.yml"


rule develop:
    shell:
        "pip install -e .[dev]"


rule docs:
    input:
        "src/",
    shell:
        'cd docs && SPHINXOPTS="-W" make html'


rule docs_clean:
    shell:
        'cd docs && SPHINXOPTS="-W" make cleanall'


rule ctags:
    input:
        nek5000="lib/Nek5000/core",
        abl="src/abl",
        snek5000="src/snek5000",
    output:
        ".tags",
    params:
        excludes=" ".join(
            (
                f"--exclude={pattern}"
                for pattern in (
                    ".snakemake",
                    "__pycache__",
                    "obj",
                    "logs",
                    "*.tar.gz",
                    "*.f?????",
                )
            )
        ),
    shell:
        """
        ctags -f {output} --language-force=Fortran -R {input.nek5000}
        ctags -f {output} {params.excludes} --append --language-force=Fortran -R {input.abl}
        ctags -f {output} {params.excludes} --append -R {input.snek5000}
        """


rule watch:
    params:
        per_second=5,
        rules="docs ctags",
    shell:
        "nohup watch -n {params.per_second} snakemake {params.rules} 2>&1 > /tmp/watch.log&"


rule release:
    shell:
        """
        rm -rf build dist
        python setup.py sdist
        twine check dist/*
        """


rule testpypi:
    shell:
        """
        twine upload --repository testpypi dist/*
        """
