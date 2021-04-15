"""Post simulation archive-creation utilities"""
import re
import shlex
import shutil
import subprocess
from glob import iglob
from pathlib import Path
from shutil import rmtree

from .. import logger
from . import modification_date


def archive(tarball, items=(), remove=False, readonly=False):
    """Archive simulation contents into a tarball / compress a tarball.

    Examples
    --------
    >>> archive("test.tar.xz", ["file1", "file2"])
    # runs tar -cvf test.tar.xz file1 file2

    >>> archive("test.tar.gz")
    # runs gzip test.tar

    """
    logger.info(repr(locals()))
    if not tarball:
        raise IOError(
            "Abort archiving because of illegal tarball name / empty input! "
            f"tarball: {tarball}, items: {items}"
        )

    # prepare output directory
    dest = Path.cwd() / "data"
    dest.mkdir(exist_ok=True)

    if items:
        cmd_output, output = exec_tar(tarball, items, remove)
    else:
        cmd_output, output = exec_compress(tarball)

    if readonly:
        output.chmod(0o444)

    return cmd_output


def clean_simul(case, tarball):
    """Clean a simulation after archiving into a tarball."""
    if tarball and not Path(tarball).exists():
        raise IOError(
            f"Archive {tarball} not found. Refusing to clean "
            "simulation files! Run 'snakemake archive'"
        )

    remove(Path(f"{case}.{ext}") for ext in "re2 ma2 log f nek5000".split())
    remove(
        Path(file)
        for file in "makefile box.tmp compiler.out SESSION.NAME GIT_REVISION.txt nek5000".split()
    )
    remove([Path("obj")])
    field_files = Path.cwd().glob(f"*{case}?.f?????")
    remove(field_files)


def exec_compress(tarball):
    tar, tarball, compress_format = parse_args_from_filename(tarball)

    if not compress_format:
        logger.error(f"Cannot compress: {tar} -> {tarball}")
        return "", tarball

    # tarball will be compressed in place when no items are provided
    main = compress_cmd(compress_format).split()
    output = next_path(tarball)

    if str(output.absolute()) != str(tarball.absolute()):
        if compress_format == ".zst":
            kwargs = ("-o", output)
            cmd = [*main, str(tar), *kwargs]
            cmd_output = subprocess.check_output(cmd)
        else:
            # do something like gzip -c file.tar > file.tar.gz using
            main.append("--stdout")
            with open(tarball, "w") as fp:
                cmd = [*main, str(tar)]
                subprocess.run(cmd, stdout=fp)

            cmd_output = ""
    else:
        cmd = [*main, str(tar)]
        cmd_output = subprocess.check_output(cmd)

    return cmd_output, output


def exec_tar(tarball, items, remove):
    tar, tarball, compress_format = parse_args_from_filename(tarball)

    if compress_format:
        output = tarball
        if tar.exists():
            raise IOError("Cannot append file items into a compressed archive!")
    else:
        output = tar

    main = shlex.split(tar_cmd(compress_format, remove=remove, append=output.exists()))

    # run command
    items = [str(i) for i in items]
    cmd = [*main, str(tar), *items]
    cmd_output = subprocess.check_output(cmd)
    return cmd_output, output


def next_path(old_path):
    """Generate a new path with an integer suffix

    Example
    -------
    >>> Path("test.txt").touch()
    >>> next_path("test.txt")
    test_1.txt # if path exists
    test.txt # if path does not exists

    """
    i = 1
    p = Path(old_path)
    while p.exists():
        # for example: remove .tar from the end, if any
        stem = p.stem
        for suffix in p.suffixes:
            stem = re.sub(f"{suffix}$", "", stem)

        p = p.parent / "".join([stem, f"_{i:02d}", *p.suffixes])
        logger.info(f"Checking if path exists: {p}")

    logger.info(f"Output path: {p}")

    return p


def parse_args_from_filename(tarball):
    tarball = Path(str(tarball))

    # split archive.tar.zst -> archive, .tar, .zst
    name, dottar, compress_format = tarball.name.partition(".tar")
    tar = tarball.parent / (name + dottar)
    return tar, tarball, compress_format


def compress_cmd(compress_format):
    compress_program = {
        ".gz": "pigz" if shutil.which("pigz") else "gzip",
        ".xz": "xz",
        ".lz4": "lz4",
        ".zst": "zstdmt --rm",
    }
    cmd = compress_program[compress_format]
    return cmd


def tar_cmd(compress_format="", remove=False, append=False):
    archive_program = {
        "": "tar",
        ".gz": f"tar --use-compress-program {compress_cmd('.gz')}",
        ".xz": "tar",
        ".lz4": "tar --use-compress-program lz4",
        ".zst": "tar --use-compress-program zstdmt",
    }
    # For benchmarking ...
    # cmd = "time " +
    cmd = archive_program[compress_format]
    if remove:
        cmd += " --remove-files "
    elif shutil.which("bsdtar"):
        # Use bsdtar if available
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
    compress_format="",
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

        return f"{subdir}/{basename}.tar{compress_format}"
    else:
        return ""


def remove(items):
    """Equivalent to rm -rf"""
    print("Removing", items)
    for item in items:
        if item.is_dir():
            rmtree(item, ignore_errors=True)
        else:
            try:
                item.unlink(missing_ok=True)
            except TypeError:
                # python < 3.8
                pass
