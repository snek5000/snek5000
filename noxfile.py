"""Task runner for the developer

Usage
-----

   nox -l

   nox -s <session>

   nox -k <keyword>
or:

   make <session>

execute ``make list-sessions```` or ``nox -l`` for a list of sessions.

"""
import os
import re
import shlex
import shutil
from functools import partial
from pathlib import Path

import nox

PACKAGE = "snek5000"
CWD = Path.cwd()
if (CWD / "poetry.lock").exists():
    BUILD_SYSTEM = "poetry"
    PACKAGE_SPEC = "pyproject.toml"
else:
    BUILD_SYSTEM = "setuptools"
    PACKAGE_SPEC = "setup.cfg"

try:
    NEK_SOURCE_ROOT = os.environ["NEK_SOURCE_ROOT"]
except KeyError:
    raise RuntimeError(
        "Environment variable NEK_SOURCE_ROOT should be set "
        "pointing to Nek5000 top level directory."
    )

TEST_ENV_VARS = {
    "NEK_SOURCE_ROOT": NEK_SOURCE_ROOT,
    "SNEK_DEBUG": "1",
}
if os.getenv("CI"):
    TEST_ENV_VARS["PYTEST_ADDOPTS"] = "--color=yes"

EXTRA_REQUIRES = ("main", "docs", "tests", "dev")

no_venv_session = partial(nox.session, venv_backend="none")
nox.options.sessions = ["tests"]


def run_ext(session, cmd):
    """Run an external command, i.e. outside a nox managed virtual envionment"""
    session.run(*shlex.split(cmd), external=True)


def rmdir(path_dir: str):
    if Path(path_dir).exists():
        shutil.rmtree(path_dir)


def poetry_install(session, *args):
    """Install with dependencies pinned in pyproject.toml"""
    run_ext(session, "python -m poetry install " + " ".join(args))


def pip_install(session, filename, *args):
    """Install with dependencies pinned in requirements/*.txt"""
    run_ext(
        session,
        f"python -m pip install -r requirements/{filename}.txt " + " ".join(args),
    )


def pip_sync(session, filename):
    """Reset developer environment with dependencies pinned in requirements/dev.txt"""
    run_ext(session, f"python -m piptools sync requirements/{filename}.txt")


@no_venv_session
def install(session):
    """Install package."""
    if BUILD_SYSTEM == "poetry":
        poetry_install(session)
    else:
        pip_install(session, "main", ".")


@no_venv_session
def develop(session):
    """Install developer environment."""
    if BUILD_SYSTEM == "poetry":
        poetry_install(session, "--with=dev")
    else:
        pip_install(session, "dev")


@no_venv_session
def sync(session):
    """Sync developer environment."""
    if BUILD_SYSTEM == "poetry":
        poetry_install(session, "--sync", "--with=dev")
    else:
        pip_sync(session, "dev")


@no_venv_session
def requires(session):
    """Pin dependencies"""
    if BUILD_SYSTEM == "poetry":
        run_ext(session, "python -m poetry lock --no-update")
    else:
        session.notify("pip-compile")


@nox.session(name="pip-compile", reuse_venv=True)
@nox.parametrize("extra", [nox.param(extra, id=extra) for extra in EXTRA_REQUIRES])
def pip_compile(session, extra):
    """Pin dependencies to requirements/*.txt

    How to run all in parallel::

        pipx install nox
        make -j requirements

    or::

        nox -l | awk '/pip-compile/{print $2}' | xargs -P6 -I_ nox -s _

    """
    session.install("pip-tools")
    req = Path("requirements")

    if extra == "main":
        in_extra = ""
        in_file = ""
    else:
        in_extra = f"--extra {extra}"
        in_file = req / "vcs_packages.in"

    out_file = req / f"{extra}.txt"

    session.run(
        *shlex.split(
            "python -m piptools compile --resolver backtracking --quiet -U "
            f"{in_extra} {in_file} {PACKAGE_SPEC} "
            f"-o {out_file}"
        ),
        *session.posargs,
    )

    session.log(f"Removing absolute paths from {out_file}")
    packages = out_file.read_text()
    rel_path_packages = packages.replace("file://" + str(Path.cwd().resolve()), ".")

    # special cases for snek5000-canonical and snek5000-tgv
    for package in ("snek5000-canonical", "snek5000-tgv"):
        rel_path_packages = rel_path_packages.replace(f"{package} @ ", "")

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


def install_with_tests(session, args=()):
    if BUILD_SYSTEM == "poetry":
        session.install("poetry")
        session.run("python", "-m", "poetry", "install", "--with=tests", *args)
        session.run("python", "-m", "poetry", "env", "info")
        return "python", "-m", "poetry", "run", "pytest"
    else:
        session.install("-r", "requirements/tests.txt", *args)
        return "python", "-m", "pytest"


@nox.session
def tests(session):
    """Execute unit-tests using pytest"""
    pytest_cmd = install_with_tests(session)
    session.run(
        *pytest_cmd,
        *session.posargs,
        env=TEST_ENV_VARS,
    )


@no_venv_session(name="tests-cov")
def tests_cov(session):
    """Execute unit-tests using pytest+pytest-cov"""
    session.notify(
        "tests",
        [
            "--cov",
            "--cov-config=pyproject.toml",
            "--no-cov-on-fail",
            "--cov-report=term-missing",
            *session.posargs,
        ],
    )


@nox.session(name="coverage-html")
def coverage_html(session, nox=False):
    """Generate coverage report in HTML. Requires `tests-cov` session."""
    report = Path.cwd() / ".coverage" / "html" / "index.html"
    session.install("coverage[toml]")
    session.run("coverage", "html")

    print("Code coverage analysis complete. View detailed report:")
    print(f"file://{report}")


@no_venv_session(name="format")
def format_(session):
    """Run pre-commit hooks on all files to set and lint code-format"""
    run_ext(session, "pre-commit install")
    run_ext(session, "pre-commit run --all-files")


@nox.session
def lint(session):
    """Run pre-commit hooks on files which differ in the current branch from origin/HEAD."""
    remote = "origin/HEAD" if not session.posargs else session.posargs[0]
    session.install("pre-commit")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "--from-ref", remote, "--to-ref", "HEAD")


def _prepare_docs_session(session):
    session.install("-r", "requirements/docs.txt")
    session.chdir("./docs")

    build_dir = Path.cwd() / "_build"
    source_dir = "."
    output_dir = str(build_dir.resolve() / "html")
    return source_dir, output_dir


@nox.session
def docs(session):
    """Build documentation using Sphinx."""
    source, output = _prepare_docs_session(session)
    session.run(
        "python", "-m", "sphinx", "-b", "html", *session.posargs, source, output
    )  # Same as sphinx-build
    print("Build finished.")
    print(f"file://{output}/index.html")


@nox.session(name="docs-autobuild")
def docs_autobuild(session):
    """Build documentation using sphinx-autobuild."""
    source, output = _prepare_docs_session(session)
    session.run(
        "python",
        "-m",
        "sphinx_autobuild",
        "--watch",
        "../src",
        "--re-ignore",
        r"(_build|generated)\/.*",
        source,
        output,
    )  # Same as sphinx-autobuild
    print("Build finished.")
    print(f"file://{output}/index.html")


@no_venv_session
def ctags(session):
    """Runs universal-ctags to build .tags file"""
    sources = {
        "nek5000": str(Path(NEK_SOURCE_ROOT) / "core"),
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
        session,
        f"ctags -f {output} --language-force=Fortran -R {sources['nek5000']}",
    )
    run_ext(session, f"ctags -f {output} {excludes} --append -R {sources['snek5000']}")


@no_venv_session
def testpypi(session):
    """Release clean, build, upload to TestPyPI"""
    session.notify("release-clean")
    session.notify("release-build")
    session.notify("release-upload", ["--repository", "testpypi"])


@no_venv_session
def pypi(session):
    """Release clean, download from TestPyPI, test, upload to PyPI"""
    session.notify("release-clean")
    # NOTE: parametrizing dist_type ends up in erraneous deduplication of sessions
    # by nox
    for dist_type in ("no-binary", "only-binary"):
        session.notify(f"download-testpypi(dist_type='{dist_type}')")
        session.notify(f"release-tests(dist_type='{dist_type}')")
    session.notify("release-upload", ["--repository", "pypi"])


@nox.session(name="download-testpypi")
@nox.parametrize("dist_type", ["no-binary", "only-binary"])
def download_testpypi(session, dist_type):
    """Download from TestPyPI and run tests"""
    (Path.cwd() / "dist").mkdir(exist_ok=True)
    session.chdir("./dist")

    git_tags = session.run(
        "git", "tag", "--list", "--sort=committerdate", external=True, silent=True
    )
    latest_version = git_tags.splitlines()[-1]
    spec = f"{PACKAGE}=={latest_version}"
    session.run(
        "python",
        "-m",
        "pip",
        "index",
        "versions",
        "--index-url",
        "https://test.pypi.org/simple",
        "--pre",
        PACKAGE,
    )
    session.run(
        "python",
        "-m",
        "pip",
        "download",
        "--index-url",
        "https://test.pypi.org/simple",
        "--extra-index-url",
        "https://pypi.org/simple",
        "--pre",
        "--no-deps",
        f"--{dist_type}",
        PACKAGE,
        spec,
    )


@nox.session(name="release-tests")
@nox.parametrize("dist_type", ["no-binary", "only-binary"])
def release_tests(session, dist_type):
    """Execute test suite with build / downloaded package in ./dist"""
    if dist_type == "only-binary":
        pattern = "*.whl"
    else:
        pattern = "*.tar.gz"

    if BUILD_SYSTEM == "poetry":
        poetry_conf = CWD / "poetry.toml"
        assert (
            not poetry_conf.exists()
        ), "Poetry local configuration exists. Please remove to continue"
        session.install("poetry")
        session.run(
            "python",
            "-m",
            "poetry",
            "config",
            "--local",
            "virtualenvs.create",
            "false",
        )
        pytest_cmd = install_with_tests(session, ["--no-root"])
    else:
        pytest_cmd = install_with_tests(session)

    dist_packages = [str(p) for p in Path("./dist").glob(pattern)]
    session.install(*dist_packages)

    try:
        session.run(
            *pytest_cmd,
            env=TEST_ENV_VARS,
        )
    finally:
        if BUILD_SYSTEM == "poetry":
            poetry_conf.unlink()


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
    session.run("twine", "check", "--strict", "dist/*")
    args = session.posargs

    # See
    # https://pypi.org/help/#apitoken and
    # https://twine.readthedocs.io/en/latest/#environment-variables
    env = {"TWINE_USERNAME": "__token__"}

    test_pypi_token = os.getenv("TEST_PYPI_TOKEN")
    pypi_token = os.getenv("PYPI_TOKEN")
    if "testpypi" in args and test_pypi_token:
        env["TWINE_PASSWORD"] = test_pypi_token
    elif pypi_token:
        env["TWINE_PASSWORD"] = pypi_token

    session.run("twine", "upload", *args, "dist/*", env=env)
