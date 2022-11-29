import os
from pathlib import Path

from snek5000.util import files


def test_next_path_no_files(tmpdir):
    tmpdir = Path(tmpdir)

    # Create no files, multiple suffixes
    target = tmpdir / "test.tar.gz"

    assert str(files.next_path(target, force_suffix=True)) == str(
        tmpdir / "test_00.tar.gz"
    )


def test_next_path_one_file(tmpdir):
    tmpdir = Path(tmpdir)

    # Create a file
    target = tmpdir / "test.txt"
    target.touch()  # Not necessary, but to see what happens.

    assert str(files.next_path(target, force_suffix=True)) == str(
        tmpdir / "test_00.txt"
    )


def test_next_path_one_file_no_suffix(tmpdir):
    tmpdir = Path(tmpdir)

    # Create a file
    target = tmpdir / "test.txt"
    target.touch()
    (tmpdir / "test_00.txt").touch()

    assert str(files.next_path(target)) == str(tmpdir / "test_01.txt")


def test_next_path_two_files(tmpdir):
    tmpdir = Path(tmpdir)

    # Create multple files
    target = tmpdir / "test.txt"
    (tmpdir / "test_00.txt").touch()
    (tmpdir / "test_01.txt").touch()

    assert str(files.next_path(target, force_suffix=True)) == str(
        tmpdir / "test_02.txt"
    )


def test_next_path_dir_no_suffix(tmpdir):
    tmpdir = Path(tmpdir)

    # Create a directory
    target = tmpdir / "test_dir"
    target.mkdir()
    (target / "foo").touch()

    assert str(files.next_path(target)) == str(tmpdir / "test_dir_00")


def test_next_path_dir(tmpdir):
    tmpdir = Path(tmpdir)

    target = tmpdir / "test_dir"
    path_dir = files.next_path(target, force_suffix=True)

    assert str(path_dir) == str(tmpdir / "test_dir_00")


def test_next_path_relative(tmpdir):
    os.chdir(tmpdir)

    session_00 = Path("./session_00")
    session_01 = Path("./session_01")

    assert files.next_path("session", force_suffix=True) == session_00

    session_00.mkdir()
    (session_00 / "foo").touch()
    int_suffix, session_dir = files.next_path(
        "session", force_suffix=True, return_suffix=True
    )

    assert int_suffix == 1
    assert session_dir == session_01

    if session_dir.is_absolute():
        raise ValueError("next_path should return a relative path")
