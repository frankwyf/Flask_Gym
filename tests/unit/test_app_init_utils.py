from pathlib import Path

from app import make_dir


def test_make_dir_creates_directory(tmp_path):
    target = tmp_path / "logs_nested"
    assert not target.exists()

    make_dir(str(target))

    assert target.exists()
    assert target.is_dir()
