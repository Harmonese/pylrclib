from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from ..config import SUPPORTED_PLAIN_EXTENSIONS, SUPPORTED_SYNCED_EXTENSIONS, UpConfig
from ..lrc import normalize_name, parse_lrc_file, read_text_any
from ..lrc.matcher import find_matching_paths, find_yaml_named_candidates, strip_known_suffixes
from ..models import LyricsBundle, LyricsRecord, TrackMeta, YamlTrackMeta

PURE_MUSIC_PHRASES = (
    "纯音乐，请欣赏",
    "纯音乐, 请欣赏",
    "纯音乐 请欣赏",
    "此歌曲为没有填词的纯音乐",
    "instrumental",
)


@dataclass(slots=True)
class ClassifiedText:
    kind: str
    plain: str = ""
    synced: str = ""
    warnings: list[str] | None = None


def _clean_plain_text(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip("\n")


def detect_plain_text(text: str) -> ClassifiedText:
    cleaned = _clean_plain_text(text)
    lowered = cleaned.lower()
    if not cleaned:
        return ClassifiedText(kind="invalid", warnings=["empty_text"])
    if any(phrase.lower() in lowered for phrase in PURE_MUSIC_PHRASES):
        return ClassifiedText(kind="instrumental", warnings=["instrumental_phrase_detected"])
    return ClassifiedText(kind="plain", plain=cleaned, warnings=[])


def classify_text(path: Path) -> ClassifiedText:
    parsed = parse_lrc_file(path)
    if parsed.has_valid_timestamps:
        kind = "instrumental" if parsed.is_instrumental else "synced"
        return ClassifiedText(kind=kind, plain=parsed.plain, synced=parsed.synced, warnings=list(parsed.warnings))
    plain = detect_plain_text(parsed.original_text)
    return plain


def _iter_candidate_dirs(config: UpConfig) -> list[Path]:
    dirs: list[Path] = []
    for candidate in [config.plain_dir, config.synced_dir, config.lyrics_dir]:
        if candidate and candidate not in dirs and candidate.exists():
            dirs.append(candidate)
    return dirs


def _add_unique(values: list[Path], seen: set[Path], path: Path) -> None:
    resolved = path.expanduser().resolve()
    if resolved.exists() and resolved.is_file() and resolved not in seen:
        seen.add(resolved)
        values.append(resolved)


def collect_candidate_paths(item, config: UpConfig) -> tuple[list[Path], list[Path]]:
    plain_candidates: list[Path] = []
    synced_candidates: list[Path] = []
    seen_plain: set[Path] = set()
    seen_synced: set[Path] = set()
    search_dirs = _iter_candidate_dirs(config)

    if item.source_kind == "yaml":
        meta = item.original_meta
        assert isinstance(meta, YamlTrackMeta)
        for path in find_yaml_named_candidates(meta, search_dirs, meta.plain_file, SUPPORTED_PLAIN_EXTENSIONS):
            _add_unique(plain_candidates, seen_plain, path)
        for explicit in [meta.synced_file, meta.lrc_file, meta.lyrics_file]:
            for path in find_yaml_named_candidates(meta, search_dirs, explicit, SUPPORTED_SYNCED_EXTENSIONS):
                _add_unique(synced_candidates, seen_synced, path)
        if meta.lyrics_file:
            for path in find_yaml_named_candidates(meta, search_dirs, meta.lyrics_file, SUPPORTED_PLAIN_EXTENSIONS):
                _add_unique(plain_candidates, seen_plain, path)
        for ext in SUPPORTED_SYNCED_EXTENSIONS:
            same = meta.path.with_suffix(ext)
            if same.exists():
                _add_unique(synced_candidates, seen_synced, same)
        for ext in SUPPORTED_PLAIN_EXTENSIONS:
            same = meta.path.with_suffix(ext)
            if same.exists():
                _add_unique(plain_candidates, seen_plain, same)

    original_path = item.original_meta.path
    if original_path is not None:
        for directory in search_dirs:
            for ext in SUPPORTED_SYNCED_EXTENSIONS:
                candidate = directory / f"{original_path.stem}{ext}"
                if candidate.exists():
                    _add_unique(synced_candidates, seen_synced, candidate)
            for ext in SUPPORTED_PLAIN_EXTENSIONS:
                candidate = directory / f"{original_path.stem}{ext}"
                if candidate.exists():
                    _add_unique(plain_candidates, seen_plain, candidate)

    meta = item.api_meta
    for path in find_matching_paths(meta, search_dirs, SUPPORTED_SYNCED_EXTENSIONS):
        _add_unique(synced_candidates, seen_synced, path)
    for path in find_matching_paths(meta, search_dirs, SUPPORTED_PLAIN_EXTENSIONS):
        _add_unique(plain_candidates, seen_plain, path)
    return plain_candidates, synced_candidates


def _choose_best_path(paths: list[Path]) -> Optional[Path]:
    return paths[0] if len(paths) == 1 else None


def _load_plain_candidate(path: Path) -> ClassifiedText:
    return classify_text(path)


def _load_synced_candidate(path: Path) -> ClassifiedText:
    return classify_text(path)


def _bundle_kind(plain: str, synced: str, instrumental: bool, warnings: list[str]) -> str:
    if instrumental:
        return "instrumental"
    if plain.strip() and synced.strip():
        return "mixed"
    if synced.strip():
        return "synced"
    if plain.strip():
        return "plain"
    if warnings:
        return "invalid"
    return "empty"


def load_local_lyrics_bundle(item, config: UpConfig) -> tuple[LyricsBundle, list[Path], list[Path]]:
    plain_candidates, synced_candidates = collect_candidate_paths(item, config)
    warnings: list[str] = []
    plain_text = ""
    synced_text = ""
    plain_path = _choose_best_path(plain_candidates)
    synced_path = _choose_best_path(synced_candidates)
    instrumental = False

    if plain_path:
        classified = _load_plain_candidate(plain_path)
        warnings.extend(classified.warnings or [])
        if classified.kind == "plain":
            plain_text = classified.plain
        elif classified.kind == "instrumental":
            instrumental = True
        elif classified.kind == "synced" and not synced_text:
            synced_text = classified.synced
            plain_text = classified.plain
            synced_path = plain_path
            plain_path = None
        else:
            warnings.append("invalid_plain_candidate")

    if synced_path:
        classified = _load_synced_candidate(synced_path)
        warnings.extend(classified.warnings or [])
        if classified.kind == "synced":
            synced_text = classified.synced
            if not plain_text and config.allow_derived_plain:
                plain_text = classified.plain
        elif classified.kind == "plain":
            if not plain_text:
                plain_text = classified.plain
                plain_path = synced_path
                synced_path = None
        elif classified.kind == "instrumental":
            instrumental = True
        else:
            warnings.append("invalid_synced_candidate")

    kind = _bundle_kind(plain_text, synced_text, instrumental, warnings)
    bundle = LyricsBundle(
        kind=kind,
        plain=plain_text,
        synced=synced_text,
        instrumental=instrumental,
        plain_path=plain_path,
        synced_path=synced_path,
        warnings=warnings,
    )
    return bundle, plain_candidates, synced_candidates


def bundle_from_record(record: LyricsRecord, *, mode: str = "auto", allow_derived_plain: bool = True) -> LyricsBundle:
    plain = record.plain.strip("\n")
    synced = record.synced.strip("\n")
    if record.instrumental:
        return LyricsBundle(kind="instrumental", instrumental=True)
    if mode == "instrumental":
        return LyricsBundle(kind="instrumental", instrumental=True)
    if mode == "plain":
        if plain:
            return LyricsBundle(kind="plain", plain=plain)
        if synced and allow_derived_plain:
            derived = "\n".join(line.split("]", 1)[1] if "]" in line else line for line in synced.splitlines()).strip("\n")
            return LyricsBundle(kind="plain", plain=derived, synced=synced if mode == "mixed" else "")
        return LyricsBundle(kind="invalid", warnings=["no_plain_lyrics"])
    if mode == "synced":
        if synced:
            return LyricsBundle(kind="synced", synced=synced, plain=plain if allow_derived_plain else "")
        return LyricsBundle(kind="invalid", warnings=["no_synced_lyrics"])
    if mode == "mixed":
        if synced and plain:
            return LyricsBundle(kind="mixed", plain=plain, synced=synced)
        if synced and allow_derived_plain:
            derived = "\n".join(line.split("]", 1)[1] if "]" in line else line for line in synced.splitlines()).strip("\n")
            return LyricsBundle(kind="mixed", plain=derived, synced=synced)
        return LyricsBundle(kind="invalid", warnings=["incomplete_mixed_lyrics"])
    if synced and plain:
        return LyricsBundle(kind="mixed", plain=plain, synced=synced)
    if synced:
        derived = plain
        if not derived and allow_derived_plain:
            derived = "\n".join(line.split("]", 1)[1] if "]" in line else line for line in synced.splitlines()).strip("\n")
        kind = "mixed" if derived else "synced"
        return LyricsBundle(kind=kind, plain=derived, synced=synced)
    if plain:
        return LyricsBundle(kind="plain", plain=plain)
    return LyricsBundle(kind="invalid", warnings=["empty_record"])
