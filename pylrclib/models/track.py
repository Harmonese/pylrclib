from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from mutagen import File as MutaFile
from mutagen.id3 import ID3NoHeaderError

from ..logging_utils import log_debug, log_error, log_warn

TAG_MAPPINGS: Dict[str, Dict[str, list[str]]] = {
    "mp3": {"title": ["TIT2"], "artist": ["TPE1"], "album": ["TALB"]},
    "m4a": {"title": ["©nam", "\xa9nam"], "artist": ["©ART", "\xa9ART"], "album": ["©alb", "\xa9alb"]},
    "aac": {"title": ["©nam", "\xa9nam"], "artist": ["©ART", "\xa9ART"], "album": ["©alb", "\xa9alb"]},
    "flac": {"title": ["TITLE", "title"], "artist": ["ARTIST", "artist"], "album": ["ALBUM", "album"]},
    "wav": {"title": ["TIT2", "TITLE", "title"], "artist": ["TPE1", "ARTIST", "artist"], "album": ["TALB", "ALBUM", "album"]},
}


@dataclass(slots=True)
class TrackMeta:
    path: Optional[Path]
    track: str
    artist: str
    album: str
    duration: int

    def __str__(self) -> str:
        return f"{self.artist} - {self.track} ({self.album}, {self.duration}s)"

    @staticmethod
    def _get_universal_tag(audio: Any, field: str, ext: str) -> Optional[str]:
        if not audio or not audio.tags:
            return None
        for key in TAG_MAPPINGS.get(ext, {}).get(field, []):
            try:
                value = audio.tags.get(key)
            except Exception as exc:
                log_debug(f"failed reading tag {key}: {exc}")
                continue
            if value is None:
                continue
            if isinstance(value, list) and value:
                return str(value[0])
            if hasattr(value, "text") and value.text:
                return str(value.text[0])
            if isinstance(value, str):
                return value
            result = str(value)
            if result:
                return result
        return None

    @classmethod
    def from_audio_file(cls, audio_path: Path) -> Optional["TrackMeta"]:
        ext = audio_path.suffix.lower().lstrip(".")
        try:
            audio = MutaFile(audio_path)
        except ID3NoHeaderError:
            log_warn(f"audio file has no tags: {audio_path}")
            return None
        except Exception as exc:
            log_error(f"failed to read audio file {audio_path}: {exc}")
            return None
        if audio is None:
            log_warn(f"unsupported or unreadable audio file: {audio_path}")
            return None
        track = cls._get_universal_tag(audio, "title", ext)
        artist = cls._get_universal_tag(audio, "artist", ext)
        album = cls._get_universal_tag(audio, "album", ext)
        if not track or not artist or not album:
            log_warn(f"incomplete tags in audio file: {audio_path}")
            return None
        duration = int(round(getattr(getattr(audio, "info", None), "length", 0) or 0))
        if duration <= 0:
            log_warn(f"invalid duration in audio file: {audio_path}")
            return None
        return cls(path=audio_path, track=track, artist=artist, album=album, duration=duration)

    @classmethod
    def from_yaml(cls, meta: "YamlTrackMeta") -> "TrackMeta":
        return cls(path=meta.path, track=meta.track, artist=meta.artist, album=meta.album, duration=meta.duration)


@dataclass(slots=True)
class YamlTrackMeta:
    path: Path
    track: str
    artist: str
    album: str
    duration: int
    lrc_file: Optional[str] = None
    plain_file: Optional[str] = None
    synced_file: Optional[str] = None
    lyrics_file: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.artist} - {self.track} ({self.album}, {self.duration}s) [yaml]"

    @classmethod
    def from_yaml_file(cls, yaml_path: Path) -> Optional["YamlTrackMeta"]:
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            log_error(f"failed to parse YAML {yaml_path}: {exc}")
            return None
        except Exception as exc:
            log_error(f"failed to read YAML {yaml_path}: {exc}")
            return None
        if not isinstance(data, dict):
            log_warn(f"YAML must contain a mapping: {yaml_path}")
            return None
        required = [data.get("track"), data.get("artist"), data.get("album"), data.get("duration")]
        if not all(required):
            log_warn(f"YAML missing required fields: {yaml_path}")
            return None
        try:
            duration = int(data["duration"])
        except (TypeError, ValueError):
            log_warn(f"invalid YAML duration: {yaml_path}")
            return None
        if duration <= 0:
            log_warn(f"invalid YAML duration: {yaml_path}")
            return None
        return cls(
            path=yaml_path,
            track=str(data["track"]),
            artist=str(data["artist"]),
            album=str(data["album"]),
            duration=duration,
            lrc_file=str(data.get("lrc_file")) if data.get("lrc_file") else None,
            plain_file=str(data.get("plain_file")) if data.get("plain_file") else None,
            synced_file=str(data.get("synced_file")) if data.get("synced_file") else None,
            lyrics_file=str(data.get("lyrics_file")) if data.get("lyrics_file") else None,
        )
