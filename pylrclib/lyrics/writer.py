from __future__ import annotations

from pathlib import Path

from ..logging_utils import log_info, log_warn
from ..lrc import normalize_name
from ..models import LyricsBundle, TrackMeta


def build_output_stem(meta: TrackMeta, *, naming: str, base_path: Path | None = None) -> str:
    if naming == "track-basename" and base_path is not None:
        return base_path.stem
    return f"{meta.artist} - {meta.track}"


def _resolve_target(base_dir: Path, stem: str, suffix: str, *, overwrite: bool, skip_existing: bool) -> Path | None:
    base_dir.mkdir(parents=True, exist_ok=True)
    target = base_dir / f"{stem}{suffix}"
    if target.exists() and skip_existing and not overwrite:
        return None
    return target


def write_lyrics_bundle(
    bundle: LyricsBundle,
    meta: TrackMeta,
    *,
    output_dir: Path,
    plain_dir: Path | None,
    synced_dir: Path | None,
    save_mode: str,
    plain_ext: str = ".txt",
    synced_ext: str = ".lrc",
    naming: str = "track-basename",
    base_path: Path | None = None,
    overwrite: bool = False,
    skip_existing: bool = True,
) -> list[Path]:
    written: list[Path] = []
    if bundle.instrumental:
        log_info(f"instrumental track; nothing written for {meta.artist} - {meta.track}")
        return written
    stem = build_output_stem(meta, naming=naming, base_path=base_path)
    want_plain = save_mode in {"plain", "both"} or (save_mode == "auto" and not bundle.has_synced)
    want_synced = save_mode in {"synced", "both"} or (save_mode == "auto" and bundle.has_synced)
    if want_synced and bundle.has_synced:
        target_dir = synced_dir or output_dir
        target = _resolve_target(target_dir, stem, synced_ext, overwrite=overwrite, skip_existing=skip_existing)
        if target is not None:
            target.write_text(bundle.synced.rstrip("\n") + "\n", encoding="utf-8")
            written.append(target)
    if want_plain and bundle.has_plain:
        target_dir = plain_dir or output_dir
        target = _resolve_target(target_dir, stem, plain_ext, overwrite=overwrite, skip_existing=skip_existing)
        if target is not None:
            target.write_text(bundle.plain.rstrip("\n") + "\n", encoding="utf-8")
            written.append(target)
    if (want_plain and not bundle.has_plain) or (want_synced and not bundle.has_synced):
        log_warn(f"requested save mode {save_mode} but matching lyric type is unavailable for {meta.artist} - {meta.track}")
    return written
