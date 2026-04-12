from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from ..models import TrackMeta, YamlTrackMeta
from .parser import normalize_name


def split_artists(text: str) -> list[str]:
    value = text.lower()
    value = re.sub(r"\bfeat\.?\s+", "<<<SEP>>>", value)
    value = re.sub(r"\bfeaturing\b", "<<<SEP>>>", value)
    value = re.sub(r"(?<!\s),(?!\s)", "<<<SEP>>>", value)
    for sep in [" x ", " X ", "×"]:
        value = value.replace(sep, "<<<SEP>>>")
    for sep in ["&", "和", "/", ";", "、", "，", "､"]:
        value = value.replace(sep, "<<<SEP>>>")
    artists = [part.strip() for part in value.split("<<<SEP>>>") if part.strip()]
    return list(dict.fromkeys(artists))


def match_artists(left: list[str], right: list[str]) -> bool:
    if not left or not right:
        return False
    left_norm = {normalize_name(value) for value in left}
    right_norm = {normalize_name(value) for value in right}
    return not left_norm.isdisjoint(right_norm)


KNOWN_SUFFIX_MARKERS = (".lyrics", ".lyric")


def strip_known_suffixes(name: str) -> str:
    lowered = name.lower()
    for marker in KNOWN_SUFFIX_MARKERS:
        if lowered.endswith(marker):
            return name[: -len(marker)]
    return name


def parse_lrc_filename(path: Path) -> tuple[list[str], str]:
    stem = strip_known_suffixes(path.stem)
    if " - " not in stem:
        return [], ""
    artist_raw, title_raw = stem.split(" - ", 1)
    return split_artists(artist_raw), normalize_name(title_raw)


def find_matching_paths(meta: TrackMeta, search_dirs: Iterable[Path], extensions: set[str]) -> list[Path]:
    title = normalize_name(meta.track)
    artists = split_artists(meta.artist)
    matches: list[Path] = []
    seen: set[Path] = set()
    for directory in search_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.suffix.lower() not in extensions or not path.is_file():
                continue
            path_resolved = path.resolve()
            if path_resolved in seen:
                continue
            lrc_artists, lrc_title = parse_lrc_filename(path)
            if not lrc_title:
                continue
            if lrc_title != title:
                continue
            if match_artists(artists, lrc_artists):
                seen.add(path_resolved)
                matches.append(path_resolved)
    return matches


def find_matching_lrcs(meta: TrackMeta, lrc_dir: Path) -> list[Path]:
    return find_matching_paths(meta, [lrc_dir], {".lrc"})


def find_yaml_named_candidates(meta: YamlTrackMeta, search_dirs: Iterable[Path], explicit_name: str | None, extensions: set[str]) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.expanduser().resolve()
        if resolved.exists() and resolved.is_file() and resolved.suffix.lower() in extensions and resolved not in seen:
            seen.add(resolved)
            candidates.append(resolved)

    if explicit_name:
        relative = meta.path.parent / explicit_name
        if relative.exists():
            add(relative)
        for directory in search_dirs:
            in_dir = directory / explicit_name
            if in_dir.exists():
                add(in_dir)
        absolute = Path(explicit_name)
        if absolute.is_absolute() and absolute.exists():
            add(absolute)
    return candidates


def find_yaml_lrc_candidates(meta: YamlTrackMeta, lrc_dir: Path) -> list[Path]:
    candidates = find_yaml_named_candidates(meta, [lrc_dir], meta.synced_file or meta.lrc_file or meta.lyrics_file, {".lrc"})
    if candidates:
        return candidates
    same_dir = meta.path.with_suffix(".lrc")
    if same_dir.exists():
        return [same_dir.resolve()]
    same_name_in_lrc_dir = lrc_dir / (meta.path.stem + ".lrc")
    if same_name_in_lrc_dir.exists():
        return [same_name_in_lrc_dir.resolve()]
    return find_matching_lrcs(TrackMeta.from_yaml(meta), lrc_dir)
