from pathlib import Path

from pylrclib.fs import cleanup_empty_dirs, move_with_dedup


def test_move_with_dedup(tmp_path: Path):
    src = tmp_path / "src" / "file.txt"
    src.parent.mkdir(parents=True)
    src.write_text("content")
    dst = tmp_path / "dst"
    moved = move_with_dedup(src, dst)
    assert moved is not None
    assert moved.exists()
    assert moved.name == "file.txt"


def test_move_with_conflict(tmp_path: Path):
    src = tmp_path / "src" / "file.txt"
    src.parent.mkdir(parents=True)
    src.write_text("new")
    dst = tmp_path / "dst"
    dst.mkdir()
    (dst / "file.txt").write_text("old")
    moved = move_with_dedup(src, dst)
    assert moved is not None
    assert moved.name == "file_dup1.txt"


def test_cleanup_empty_dirs(tmp_path: Path):
    (tmp_path / "a" / "b").mkdir(parents=True)
    cleanup_empty_dirs(tmp_path)
    assert not (tmp_path / "a").exists()
