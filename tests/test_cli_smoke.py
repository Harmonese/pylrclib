from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path



def _run(project_root: Path, *args: str, env=None) -> subprocess.CompletedProcess[str]:
    effective_env = os.environ.copy()
    effective_env["PYTHONPATH"] = str(project_root)
    if env:
        effective_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "pylrclib", *args],
        cwd=project_root,
        env=effective_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_up_yaml_mixed_upload_smoke(tmp_path: Path, lrclib_server):
    api_base, state = lrclib_server
    project_root = Path(__file__).resolve().parents[1]
    tracks = tmp_path / "tracks"
    plain_dir = tmp_path / "plain"
    synced_dir = tmp_path / "synced"
    done_lrc = tmp_path / "done_lrc"
    tracks.mkdir()
    plain_dir.mkdir()
    synced_dir.mkdir()
    (tracks / "song.yaml").write_text(
        "track: Song Title\nartist: Artist Name\nalbum: Album Name\nduration: 180\nplain_file: song.txt\nsynced_file: song.lrc\n",
        encoding="utf-8",
    )
    (plain_dir / "song.txt").write_text("Hello world\nSecond line\n", encoding="utf-8")
    (synced_dir / "song.lrc").write_text("[00:01.00]Hello world\n[00:02.00]Second line\n", encoding="utf-8")
    result = _run(
        project_root,
        "up",
        "--tracks", str(tracks),
        "--plain-dir", str(plain_dir),
        "--synced-dir", str(synced_dir),
        "--done-lrc", str(done_lrc),
        "--lyrics-mode", "auto",
        "--yes",
        "--api-base", api_base,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert len(state["publish_requests"]) == 1
    payload = state["publish_requests"][0]["payload"]
    assert payload["plainLyrics"] == "Hello world\nSecond line"
    assert payload["syncedLyrics"] == "[00:01.00]Hello world\n[00:02.00]Second line"
    assert (done_lrc / "song.lrc").exists()
    assert (tracks / "song.yaml").exists()


def test_up_plain_only_auto_strategy_smoke(tmp_path: Path, lrclib_server):
    api_base, state = lrclib_server
    project_root = Path(__file__).resolve().parents[1]
    tracks = tmp_path / "tracks"
    plain_dir = tmp_path / "plain"
    tracks.mkdir()
    plain_dir.mkdir()
    (tracks / "song.yaml").write_text(
        "track: Song Title\nartist: Artist Name\nalbum: Album Name\nduration: 180\nplain_file: song.txt\n",
        encoding="utf-8",
    )
    (plain_dir / "song.txt").write_text("Only plain lyrics\n", encoding="utf-8")
    result = _run(
        project_root,
        "up",
        "--tracks", str(tracks),
        "--plain-dir", str(plain_dir),
        "--lyrics-mode", "auto",
        "--yes",
        "--api-base", api_base,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert len(state["publish_requests"]) == 1
    payload = state["publish_requests"][0]["payload"]
    assert payload["plainLyrics"] == "Only plain lyrics"
    assert "syncedLyrics" not in payload


def test_down_both_smoke(tmp_path: Path):
    from tests.conftest import fake_lrclib_server

    project_root = Path(__file__).resolve().parents[1]
    with fake_lrclib_server(
        external_payload={
            "plainLyrics": "Hello world\nSecond line",
            "syncedLyrics": "[00:01.00]Hello world\n[00:02.00]Second line",
            "instrumental": False,
            "duration": 180,
        }
    ) as (api_base, _state):
        out = tmp_path / "out"
        result = _run(
            project_root,
            "down",
            "--artist", "Artist Name",
            "--title", "Song Title",
            "--album", "Album Name",
            "--duration", "180",
            "--output-dir", str(out),
            "--save-mode", "both",
            "--yes",
            "--api-base", api_base,
        )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (out / "Artist Name - Song Title.lrc").exists()
    assert (out / "Artist Name - Song Title.txt").exists()


def test_cleanse_smoke(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    lrc = tmp_path / "Artist - Song.lrc"
    lrc.write_text("[00:00.00]作词：someone\n[00:01.00]Hello\n[00:01.00]你好\n", encoding="utf-8")
    result = _run(project_root, "cleanse", str(tmp_path), "--write")
    assert result.returncode == 0
    assert lrc.read_text(encoding="utf-8") == "[00:01.00]Hello"


def test_inspect_smoke(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    tracks = tmp_path / "tracks"
    plain_dir = tmp_path / "plain"
    synced_dir = tmp_path / "synced"
    tracks.mkdir()
    plain_dir.mkdir()
    synced_dir.mkdir()
    (tracks / "song.yaml").write_text(
        "track: Song Title\nartist: Artist Name\nalbum: Album Name\nduration: 180\nplain_file: song.txt\nsynced_file: song.lrc\n",
        encoding="utf-8",
    )
    (plain_dir / "song.txt").write_text("Hello world\n", encoding="utf-8")
    (synced_dir / "song.lrc").write_text("[00:00.00]Hello world\n", encoding="utf-8")
    result = _run(project_root, "inspect", "--tracks", str(tracks), "--plain-dir", str(plain_dir), "--synced-dir", str(synced_dir))
    assert result.returncode == 0
    assert "Found 1 item(s)." in result.stdout
    assert "resolved_kind=mixed" in result.stdout


def test_doctor_smoke(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
    tracks = tmp_path / "tracks"
    plain_dir = tmp_path / "plain"
    synced_dir = tmp_path / "synced"
    tracks.mkdir()
    plain_dir.mkdir()
    synced_dir.mkdir()
    result = _run(project_root, "doctor", "--tracks", str(tracks), "--plain-dir", str(plain_dir), "--synced-dir", str(synced_dir))
    assert result.returncode == 0
    assert "Resolved configuration:" in result.stdout
    assert "Found audio=0, yaml=0" in result.stdout


def test_down_by_lrclib_id_smoke(tmp_path: Path):
    from tests.conftest import fake_lrclib_server

    project_root = Path(__file__).resolve().parents[1]
    with fake_lrclib_server(
        by_id_payloads={
            "123": {
                "id": 123,
                "trackName": "Song Title",
                "artistName": "Artist Name",
                "albumName": "Album Name",
                "duration": 180,
                "plainLyrics": "Hello world\nSecond line",
                "syncedLyrics": "[00:01.00]Hello world\n[00:02.00]Second line",
                "instrumental": False,
            }
        }
    ) as (api_base, _state):
        out = tmp_path / "out"
        result = _run(
            project_root,
            "down",
            "--lrclib-id", "123",
            "--output-dir", str(out),
            "--save-mode", "both",
            "--yes",
            "--api-base", api_base,
        )
    assert result.returncode == 0, result.stderr + result.stdout
    assert (out / "Artist Name - Song Title.lrc").exists()
    assert (out / "Artist Name - Song Title.txt").exists()


def test_search_smoke(tmp_path: Path):
    from tests.conftest import fake_lrclib_server

    project_root = Path(__file__).resolve().parents[1]
    with fake_lrclib_server(
        search_payload=[
            {
                "id": 42,
                "trackName": "Song Title",
                "artistName": "Artist Name",
                "albumName": "Album Name",
                "duration": 180,
                "plainLyrics": "Hello world",
                "syncedLyrics": "[00:01.00]Hello world",
                "instrumental": False,
            }
        ]
    ) as (api_base, _state):
        result = _run(
            project_root,
            "search",
            "--query", "song title",
            "--api-base", api_base,
            "--preview-lines", "2",
        )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "#42 Artist Name - Song Title [Album Name] (180s)" in result.stdout
    assert "--- plainLyrics ---" in result.stdout
