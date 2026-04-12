from pathlib import Path

from pylrclib.lrc import cleanse_lrc_file, normalize_name, parse_lrc_file
from pylrclib.lyrics import detect_plain_text


def test_normalize_name_nfkc():
    assert normalize_name("Ａｂｃ（测试）") == "abc(测试)"


def test_parse_lrc_detects_instrumental(tmp_path: Path):
    path = tmp_path / "song.lrc"
    path.write_text("[00:00.00]纯音乐，请欣赏\n[00:05.00]Hello")
    parsed = parse_lrc_file(path)
    assert parsed.is_instrumental is True
    assert "纯音乐" not in parsed.synced


def test_cleanse_invalid_does_not_overwrite(tmp_path: Path):
    path = tmp_path / "bad.lrc"
    original = "this is not a valid lrc"
    path.write_text(original)
    result = cleanse_lrc_file(path, write=True)
    assert result.status == "invalid"
    assert path.read_text() == original


def test_detect_plain_text():
    detected = detect_plain_text("\nHello\nWorld\n")
    assert detected.kind == "plain"
    assert detected.plain == "Hello\nWorld"
