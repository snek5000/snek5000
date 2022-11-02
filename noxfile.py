"""Task runner for the developer

Usage
-----

   nox -s <session>

or:

   make <session>

execute ``make list-sessions```` or ``nox -l`` for a list of sessions.

"""
import re
import shlex
import shutil
from functools import partial
from pathlib import Path

import nox

no_venv_session = partial(nox.session, venv_backend="none")


def run_ext(session, cmd):
    """Run an external command, i.e. outside a nox managed virtual envionment"""
    session.run(*shlex.split(cmd), external=True)


def rmdir(path_dir: str):
    if Path(path_dir).exists():
        shutil.rmtree(path_dir)


@no_venv_session(name="pip-install")
def pip_install(session):
    """Install developer environment with dependencies pinned in requirements/dev.txt"""
    run_ext(session, "python -m pip install -r requirements/dev.txt")


@no_venv_session(name="pip-sync")
def pip_sync(session):
    """Reset developer environment with dependencies pinned in requirements/dev.txt"""
    run_ext(session, "python -m piptools sync requirements/dev.txt")


@nox.session(name="pip-compile", reuse_venv=True)
@nox.parametrize(
    "extra", [nox.param(extra, id=extra) for extra in ("main", "docs", "tests", "dev")]
)
def pip_compile(session, extra):
    """Pin dependencies to requirements/*.txt

    How to run all in parallel::

        pipx install nox
        make -j requirements

    """
    session.install("pip-tools")
    req = Path("requirements")
    in_package = "setup.cfg"

    if extra == "main":
        in_extra = ""
        in_file = ""
        out_file = req / "main.txt"
    else:
        in_extra = f"--extra {extra}"
        in_file = req / "vcs_packages.in"
        out_file = req / f"{extra}.txt"

    session.run(
        *shlex.split(
            "python -m piptools compile --resolver backtracking --quiet "
            f"{in_extra} {in_file} {in_package} "
            f"-o {out_file}"
        )
    )

    session.log(f"Removing absolute paths from {out_file}")
    packages = out_file.read_text()
    rel_path_packages = packages.replace("file://" + str(Path.cwd().resolve()), ".")
    if extra == "tests":
        tests_editable = out_file.parent / out_file.name.replace(
            "tests", "tests-editable"
        )
        session.log(f"Copying {out_file} with -e flag in {tests_editable}")
        tests_editable.write_text(rel_path_packages)
        session.log(f"Removing -e flag in {out_file}")
        rel_path_packages = re.sub(r"^-e\ \.", ".", rel_path_packages, flags=re.M)

    session.log(f"Writing {out_file}")
    out_file.write_text(rel_path_packages)


@nox.session
def tests(session):
    """Execute unit-tests using pytest with requirements/tests.txt"""
    session.install("-r", "requirements/tests.txt")
    session.run(
        "pytest",
        *session.posargs,
        env={"NEK_SOURCE_ROOT": str(Path.cwd() / "lib" / "Nek5000"), "SNEK_DEBUG": "1"},
    )


@nox.session(name="tests-cov")
def tests_cov(session):
    """Execute unit-tests using pytest+coverage with requirements/tests-cov.txt"""
    session.install("-r", "requirements/tests.txt")
    session.run(
        "pytest",
        "--cov",
        "--cov-config=pyproject.toml",
        "--no-cov-on-fail",
        "--cov-report=term-missing",
        *session.posargs,
        env={"NEK_SOURCE_ROOT": str(Path.cwd() / "lib" / "Nek5000"), "SNEK_DEBUG": "1"},
    )


@nox.session(name="coverage-html")
def coverage_html(session, nox=False):
    """Generate coverage report in HTML. Requires `tests-cov` session."""
    report = Path.cwd() / ".coverage" / "html" / "index.html"
    session.install("coverage[toml]")
    session.run("coverage", "html")

    print("Code coverage analysis complete. View detailed report:")
    print(f"file://{report}")


@no_venv_session(name="format-lint")
def format_lint(session):
    """Run pre-commit hooks on all files"""
    run_ext(session, "pre-commit install")
    run_ext(session, "pre-commit run --all-files")


@nox.session
def docs(session):
    """Build documentation using Sphinx."""
    session.install("-r", "requirements/docs.txt")
    session.chdir("./docs")

    build_dir = Path.cwd() / "_build"
    source_dir = "."
    output_dir = str(build_dir.resolve() / "html")

    session.run("sphinx-build", "-b", "html", source_dir, output_dir)
    print("Build finished.")
    print(f"file://{output_dir}/index.html")


@no_venv_session
def ctags(session):
    """Runs universal-ctags to build .tags file"""
    sources = {
        "nek5000": "lib/Nek5000/core",
        "snek5000": "src/snek5000",
    }
    output = ".tags"
    excludes = " ".join(
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
    )
    run_ext(
        session, f"ctags -f {output} --language-force=Fortran -R {sources['nek5000']}"
    )
    run_ext(session, f"ctags -f {output} {excludes} --append -R {sources['snek5000']}")


@no_venv_session
def release(session):
    """Release clean, build, upload"""
    session.notify("release-clean")
    session.notify("release-build")
    session.notify("release-upload", session.posargs)


@no_venv_session(name="release-clean")
def release_clean(session):
    """Remove build and dist directories"""
    session.log("Removing build and dist")
    rmdir("./build/")
    rmdir("./dist/")


@nox.session(name="release-build")
def release_build(session):
    """Build package into dist."""
    session.install("build")
    session.run("python", "-m", "build")


@nox.session(name="release-upload")
def release_upload(session):
    """Upload dist/* to repository testpypi (default, must be configured in ~/.pypirc).
    Also accepts positional arguments to `twine upload` command.

    """
    session.install("twine")
    session.run("twine", "check", "dist/*")
    if session.posargs:
        args = session.posargs
    else:
        args = "--repository", "testpypi"

    session.run("twine", "upload", *args, "dist/*")
