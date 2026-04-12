from pathlib import Path

from pylrclib.lrc import find_matching_lrcs, find_matching_paths, match_artists, parse_lrc_filename, split_artists
from pylrclib.models import TrackMeta


def test_split_artists():
    result = split_artists("A & B feat. C")
    assert result == ["a", "b", "c"]


def test_match_artists():
    assert match_artists(["A", "B"], ["b", "c"]) is True
    assert match_artists(["A"], ["c"]) is False


def test_parse_lrc_filename(tmp_path: Path):
    path = tmp_path / "Artist - Song - Remix.lrc"
    path.touch()
    artists, title = parse_lrc_filename(path)
    assert artists == ["artist"]
    assert title == "song - remix"


def test_find_matching_lrcs(tmp_path: Path):
    (tmp_path / "Artist - Song.lrc").write_text("[00:00.00]hi")
    meta = TrackMeta(path=tmp_path / "song.mp3", track="Song", artist="Artist", album="Album", duration=180)
    matches = find_matching_lrcs(meta, tmp_path)
    assert len(matches) == 1


def test_find_matching_plain_paths(tmp_path: Path):
    (tmp_path / "Artist - Song.txt").write_text("hello")
    meta = TrackMeta(path=tmp_path / "song.mp3", track="Song", artist="Artist", album="Album", duration=180)
    matches = find_matching_paths(meta, [tmp_path], {".txt"})
    assert len(matches) == 1
