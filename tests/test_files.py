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

    assert str(files.next_path(target)) == str(tmpdir / "test_dir_00")


def test_next_path_dir(tmpdir):
    tmpdir = Path(tmpdir)

    target = tmpdir / "test_dir"

    assert str(files.next_path(target, force_suffix=True)) == str(
        tmpdir / "test_dir_00"
    )
