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
from concurrent.futures import ThreadPoolExecutor as Pool
from functools import partial
from pathlib import Path

import nox

no_venv_session = partial(nox.session, venv_backend="none")


def run_ext(session, cmd):
    """Run an external command, i.e. outside a nox managed virtual envionment"""
    session.run(*shlex.split(cmd), external=True)


@no_venv_session(name="pip-install")
def pip_install(session):
    """Install developer environment with dependencies pinned in requirements/dev.txt"""
    run_ext(session, "python -m pip install -r requirements/dev.txt")


@no_venv_session(name="pip-sync")
def pip_sync(session):
    """Reset developer environment with dependencies pinned in requirements/dev.txt"""
    run_ext(session, "python -m piptools sync requirements/dev.txt")


@nox.session(name="pip-compile", reuse_venv=True)
def pip_compile(session):
    """Upgrade and pin dependencies"""
    session.install("pip-tools")
    req = Path("requirements")
    in_package = "setup.cfg"
    futures = []

    with Pool(max_workers=4) as executor:
        for extra in (None, "docs", "tests", "dev"):
            if extra:
                in_extra = f"--extra {extra}"
                in_file = req / "vcs_packages.in"
                out_file = req / f"{extra}.txt"
            else:
                in_extra = ""
                in_file = ""
                out_file = req / "main.txt"
            futures.append(
                executor.submit(
                    session.run,
                    *shlex.split(
                        "python -m piptools compile --resolver backtracking --quiet "
                        f"{in_extra} {in_file} {in_package} "
                        f"-o {out_file}"
                    ),
                )
            )
        assert all(run.result() for run in futures)

    session.log("Removing absolute paths from txt files")
    for txt in req.glob("*.txt"):
        packages = txt.read_text()
        rel_path_packages = packages.replace("file://" + str(Path.cwd().resolve()), ".")
        if txt.name == "tests.txt":
            tests_editable = txt.parent / txt.name.replace("tests", "tests-editable")
            tests_editable.write_text(rel_path_packages)
            rel_path_no_editable_packages = re.sub(
                r"^-e\ \.", ".", rel_path_packages, flags=re.M
            )
            txt.write_text(rel_path_no_editable_packages)
        else:
            txt.write_text(rel_path_packages)


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
