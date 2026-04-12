from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..api import ApiClient
from ..config import DownConfig
from ..discovery import discover_inputs
from ..interaction import Interaction
from ..logging_utils import log_info, log_warn
from ..lyrics import bundle_from_record, write_lyrics_bundle
from ..models import LyricsRecord, TrackMeta
from .up import preview


@dataclass(slots=True)
class DownloadItem:
    meta: TrackMeta
    source_kind: str
    base_path: Path | None = None

    @property
    def label(self) -> str:
        return f'[{self.source_kind}] {self.meta}'


def _meta_from_record(record: LyricsRecord) -> TrackMeta:
    return TrackMeta(
        path=None,
        track=record.track_name or '',
        artist=record.artist_name or '',
        album=record.album_name or '',
        duration=record.duration or 0,
    )


def _discover_items(config: DownConfig) -> list[DownloadItem]:
    if config.lrclib_id is not None:
        return [DownloadItem(meta=TrackMeta(path=None, track='', artist='', album='', duration=0), source_kind='id', base_path=None)]
    if config.tracks_dir is None:
        meta = TrackMeta(path=None, track=config.track or '', artist=config.artist or '', album=config.album or '', duration=config.duration or 0)
        return [DownloadItem(meta=meta, source_kind='manual', base_path=None)]
    return [DownloadItem(meta=item.api_meta, source_kind=item.source_kind, base_path=item.original_meta.path) for item in discover_inputs(config.tracks_dir)]


def _default_naming(item: DownloadItem, config: DownConfig) -> str:
    if config.naming == 'auto':
        return 'track-basename' if item.base_path is not None else 'artist-title'
    return config.naming


def run_down(config: DownConfig) -> int:
    interaction = Interaction(interactive=config.common.interactive, assume_yes=config.common.assume_yes)
    client = ApiClient(config.common)
    items = _discover_items(config)
    if not items:
        log_warn('no supported audio or YAML files found')
        return 0
    written_total = 0
    for item in items:
        log_info(f'downloading for {item.label}')
        result = None
        if config.lrclib_id is not None:
            record = client.get_by_id(config.lrclib_id)
            if record is not None:
                result = type('Obj', (), {'record': record, 'duration_ok': True, 'duration_diff': None})()
                item.meta = _meta_from_record(record)
        else:
            result = client.get_external(item.meta)
        if not result or not result.record:
            log_warn(f'no lyrics found for {item.label}')
            continue
        bundle = bundle_from_record(result.record, mode='mixed' if config.save_mode == 'both' else 'auto', allow_derived_plain=config.allow_derived_plain)
        preview('remote plainLyrics', bundle.plain, config.common.preview_lines)
        preview('remote syncedLyrics', bundle.synced, config.common.preview_lines)
        if getattr(result, 'duration_ok', True) is False and item.meta.duration > 0:
            if not interaction.confirm(f'Duration differs by {result.duration_diff}s for {item.meta.track}. Save anyway?', default=False):
                continue
        if bundle.instrumental:
            log_info(f'instrumental track reported by LRCLIB: {item.meta.artist} - {item.meta.track}')
            continue
        written = write_lyrics_bundle(
            bundle,
            item.meta,
            output_dir=config.output_dir,
            plain_dir=config.plain_dir,
            synced_dir=config.synced_dir,
            save_mode=config.save_mode,
            naming=_default_naming(item, config),
            base_path=item.base_path,
            overwrite=config.overwrite,
            skip_existing=config.skip_existing,
        )
        for path in written:
            log_info(f'wrote {path}')
        written_total += len(written)
    log_info(f'download finished: {written_total} file(s) written')
    return 0
