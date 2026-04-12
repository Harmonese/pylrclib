from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

LRCLIB_BASE = "https://lrclib.net/api"
DEFAULT_USER_AGENT = "pylrclib/1.1.0"
PREVIEW_LINES_DEFAULT = 10
MAX_HTTP_RETRIES_DEFAULT = 5
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".flac", ".wav"}
SUPPORTED_YAML_EXTENSIONS = {".yaml", ".yml"}
SUPPORTED_SYNCED_EXTENSIONS = {".lrc"}
SUPPORTED_PLAIN_EXTENSIONS = {".txt", ".lyrics", ".lyric"}
UNSET = object()


@dataclass(slots=True)
class CommonOptions:
    lang: str
    preview_lines: int
    max_http_retries: int
    user_agent: str
    lrclib_base: str
    interactive: bool = True
    assume_yes: bool = False


@dataclass(slots=True)
class UpConfig:
    tracks_dir: Path
    lyrics_dir: Optional[Path]
    plain_dir: Optional[Path]
    synced_dir: Optional[Path]
    done_tracks_dir: Optional[Path]
    done_lrc_dir: Optional[Path]
    follow_track: bool
    rename_lrc: bool
    cleanse: bool
    cleanse_write: bool
    allow_non_lrc: bool
    ignore_duration_mismatch: bool
    lyrics_mode: str
    allow_derived_plain: bool
    mode: str
    common: CommonOptions


@dataclass(slots=True)
class DownConfig:
    tracks_dir: Optional[Path]
    output_dir: Path
    plain_dir: Optional[Path]
    synced_dir: Optional[Path]
    save_mode: str
    skip_existing: bool
    overwrite: bool
    naming: str
    artist: Optional[str]
    track: Optional[str]
    album: Optional[str]
    duration: Optional[int]
    allow_derived_plain: bool
    common: CommonOptions


def env_or_default(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def resolve_path(value: object, env_name: str, fallback: Optional[Path] = None) -> Optional[Path]:
    if value is UNSET:
        env_value = env_or_default(env_name)
        if env_value:
            return Path(env_value).expanduser().resolve()
        if fallback is None:
            return None
        return fallback.expanduser().resolve()
    if value is None:
        return None
    return Path(str(value)).expanduser().resolve()


def resolve_int(value: object, env_name: str, default: int) -> int:
    if value is UNSET:
        env_value = env_or_default(env_name)
        if env_value is not None:
            try:
                return int(env_value)
            except ValueError:
                return default
        return default
    return int(value)


def resolve_optional_int(value: object, env_name: str) -> Optional[int]:
    if value is UNSET:
        env_value = env_or_default(env_name)
        if env_value in {None, ""}:
            return None
        try:
            return int(env_value)
        except ValueError:
            return None
    if value in {None, ""}:
        return None
    return int(value)


def resolve_str(value: object, env_name: str, default: str) -> str:
    if value is UNSET:
        return env_or_default(env_name, default) or default
    return str(value)


def resolve_optional_str(value: object, env_name: str) -> Optional[str]:
    if value is UNSET:
        env_value = env_or_default(env_name)
        return env_value or None
    if value in {None, ""}:
        return None
    return str(value)
