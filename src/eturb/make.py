"""Snakemake interface
======================

"""
import subprocess
from glob import iglob
from pathlib import Path
from shutil import rmtree

from snakemake import snakemake
from snakemake.executors import change_working_directory as change_dir

from .util import modification_date


def tar_cmd(compress_format="zst", remove=False, append=False):
    compress_program = {
        "gz": "tar --use-compress-program pigz",
        "xz": "tar",
        "lz4": "tar --use-compress-program lz4",
        "zst": "tar --use-compress-program zstdmt",
    }
    # For benchmarking ...
    # cmd = "time " +
    cmd = compress_program[compress_format]
    if remove:
        cmd += " --remove-files "
    else:
        # bsdtar is faster, but does not support --remove-files option
        cmd = "bsdtar"

    if append:
        return cmd + " --append --file"
    else:
        # create new tarball
        return cmd + " -cvf"


def tar_name(
    root_name="abl",
    pattern="*.f?????",
    compress_format="zst",
    subdir="data",
    default_prefix="test",
):
    """Generate a tarball name based on contents of current working
    directory.

    """
    modified_dates = [modification_date(f) for f in iglob(pattern)]
    cwd = Path.cwd().name
    if modified_dates:
        if cwd == root_name:
            timestamp = max(modified_dates)
            basename = f"{default_prefix}-{timestamp}"
        else:
            basename = cwd

        return f"{subdir}/{basename}.tar.{compress_format}"
    else:
        return ""


def archive(tarball, items, remove=False):
    """Archive simulation contents into a tarball."""
    # if the tarball already exists
    tarball = str(tarball)
    append = Path(tarball).exists()
    tar = tar_cmd(remove=remove, append=append).split()

    # prepare output directory
    dest = Path.cwd() / "data"
    dest.mkdir(exist_ok=True)

    # run
    items = [str(i) for i in items]
    if items:
        cmd = [*tar, tarball, *items]
        return subprocess.check_output(cmd)


def clean_simul(case, tarball):
    """Clean a simulation after archiving into a tarball."""
    if tarball and not Path(tarball).exists():
        raise IOError(
            f"Archive {tarball} not found. Refusing to clean "
            "simulation files! Run 'snakemake archive'"
        )

    def remove(items):
        """Equivalent to rm -rf"""
        print("Removing", items)
        for item in items:
            if item.is_dir():
                rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)

    remove(Path(f"{case}.{ext}") for ext in "re2 ma2 log f nek5000".split())
    remove(
        Path(file)
        for file in "makefile box.tmp compiler.out SESSION.NAME GIT_REVISION.txt nek5000".split()
    )
    remove([Path("obj")])
    field_files = Path.cwd().glob(f"*{case}?.f?????")
    remove(field_files)


class Make:
    """Snakemake interface for the solvers.

    :param sim: A simulation instance

    """

    def __init__(self, sim):
        self.sim = sim
        self.path_run = sim.output.path_run
        try:
            self.file = next(
                f for f in sim.output.get_paths() if f.name == "Snakefile"
            )
        except AttributeError:
            raise AttributeError(
                "Unable to get path of Snakefile via Output class."
            )

    def list(self):
        """List rules."""
        with change_dir(self.path_run):
            return snakemake(self.file, listrules=True)

    def exec(self, rules=("run",), dryrun=False):
        """Execute snakemake rules in sequence.

        :returns: True if workflow execution was successful.

        """
        with change_dir(self.path_run):
            return snakemake(self.file, targets=rules, dryrun=dryrun)
