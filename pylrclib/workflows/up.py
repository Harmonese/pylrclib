from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..api import ApiClient
from ..config import UpConfig
from ..discovery import InputItem, discover_inputs
from ..fs import cleanup_empty_dirs, move_with_dedup
from ..interaction import Interaction
from ..logging_utils import log_error, log_info, log_warn
from ..lyrics import bundle_from_record, collect_candidate_paths, load_local_lyrics_bundle
from ..models import LyricsBundle, LookupResult, LyricsRecord, TrackMeta


@dataclass(slots=True)
class UploadPlan:
    mode: str
    plain: Optional[str]
    synced: Optional[str]
    reason: str


def preview(label: str, text: str, max_lines: int) -> None:
    print(f'--- {label} ---')
    if not text:
        print('[empty]')
        print('-' * 40)
        return
    lines = text.splitlines()
    for line in lines[:max_lines]:
        print(line)
    if len(lines) > max_lines:
        print(f'... ({len(lines)} lines total)')
    print('-' * 40)


def resolve_lyrics_candidates(item: InputItem, config: UpConfig) -> tuple[list[Path], list[Path]]:
    return collect_candidate_paths(item, config)


def _bundle_kind(bundle: LyricsBundle) -> str:
    if bundle.instrumental:
        return 'instrumental'
    if bundle.plain and bundle.synced:
        return 'mixed'
    if bundle.synced:
        return 'synced'
    if bundle.plain:
        return 'plain'
    return 'invalid'


def resolve_local_bundle(item: InputItem, config: UpConfig, interaction: Interaction) -> tuple[LyricsBundle, list[Path], list[Path]]:
    bundle, plain_candidates, synced_candidates = load_local_lyrics_bundle(item, config)
    if bundle.kind != 'empty':
        return bundle, plain_candidates, synced_candidates

    from ..lyrics.loader import classify_text
    if plain_candidates or synced_candidates:
        selected_plain = interaction.choose_value('Multiple plain lyric candidates found:', plain_candidates)
        selected_synced = interaction.choose_value('Multiple synced lyric candidates found:', synced_candidates)
        if selected_plain is None and plain_candidates:
            selected_plain = plain_candidates[0]
        if selected_synced is None and synced_candidates:
            selected_synced = synced_candidates[0]
        selected_bundle = LyricsBundle.empty()
        if selected_plain:
            classified = classify_text(selected_plain)
            if classified.kind == 'plain':
                selected_bundle.plain = classified.plain
                selected_bundle.plain_path = selected_plain
            elif classified.kind == 'instrumental':
                selected_bundle.instrumental = True
        if selected_synced:
            classified = classify_text(selected_synced)
            if classified.kind == 'synced':
                selected_bundle.synced = classified.synced
                selected_bundle.synced_path = selected_synced
                if not selected_bundle.plain and config.allow_derived_plain:
                    selected_bundle.plain = classified.plain
            elif classified.kind == 'plain' and not selected_bundle.plain:
                selected_bundle.plain = classified.plain
                selected_bundle.plain_path = selected_synced
            elif classified.kind == 'instrumental':
                selected_bundle.instrumental = True
        selected_bundle.kind = _bundle_kind(selected_bundle)
        return selected_bundle, plain_candidates, synced_candidates

    plain_manual: Optional[Path] = None
    synced_manual: Optional[Path] = None
    while True:
        action = interaction.missing_lyrics_action()
        if action == 'skip':
            return LyricsBundle.empty(), plain_candidates, synced_candidates
        if action == 'quit':
            raise SystemExit(1)
        if action == 'instrumental':
            return LyricsBundle(kind='instrumental', instrumental=True), plain_candidates, synced_candidates
        if action == 'plain':
            plain_manual = interaction.manual_path(expected='plain lyrics')
        if action == 'synced':
            synced_manual = interaction.manual_path(expected='synced lyrics')
        if plain_manual or synced_manual:
            plain_candidates = ([plain_manual] if plain_manual else []) + plain_candidates
            synced_candidates = ([synced_manual] if synced_manual else []) + synced_candidates
            manual_bundle = LyricsBundle.empty()
            if plain_manual:
                classified = classify_text(plain_manual)
                if classified.kind == 'plain':
                    manual_bundle.plain = classified.plain
                    manual_bundle.plain_path = plain_manual
                elif classified.kind == 'instrumental':
                    manual_bundle.instrumental = True
            if synced_manual:
                classified = classify_text(synced_manual)
                if classified.kind == 'synced':
                    manual_bundle.synced = classified.synced
                    manual_bundle.synced_path = synced_manual
                    if not manual_bundle.plain and config.allow_derived_plain:
                        manual_bundle.plain = classified.plain
                elif classified.kind == 'plain' and not manual_bundle.plain:
                    manual_bundle.plain = classified.plain
                    manual_bundle.plain_path = synced_manual
                elif classified.kind == 'instrumental':
                    manual_bundle.instrumental = True
            manual_bundle.kind = _bundle_kind(manual_bundle)
            return manual_bundle, plain_candidates, synced_candidates


def build_upload_plan(bundle: LyricsBundle, *, mode: str, allow_derived_plain: bool) -> UploadPlan:
    if bundle.instrumental or mode == 'instrumental':
        return UploadPlan(mode='instrumental', plain=None, synced=None, reason='instrumental')
    plain = bundle.plain.strip()
    synced = bundle.synced.strip()
    if mode == 'plain':
        if plain:
            return UploadPlan(mode='lyrics', plain=plain, synced=None, reason='plain_only')
        return UploadPlan(mode='skip', plain=None, synced=None, reason='plain_unavailable')
    if mode == 'synced':
        if synced:
            return UploadPlan(mode='lyrics', plain=plain if allow_derived_plain else None, synced=synced, reason='synced_only')
        return UploadPlan(mode='skip', plain=None, synced=None, reason='synced_unavailable')
    if mode == 'mixed':
        if synced and plain:
            return UploadPlan(mode='lyrics', plain=plain, synced=synced, reason='mixed_only')
        return UploadPlan(mode='skip', plain=None, synced=None, reason='mixed_incomplete')
    if synced and plain:
        return UploadPlan(mode='lyrics', plain=plain, synced=synced, reason='auto_mixed')
    if synced:
        return UploadPlan(mode='lyrics', plain=plain if allow_derived_plain else None, synced=synced, reason='auto_synced')
    if plain:
        return UploadPlan(mode='lyrics', plain=plain, synced=None, reason='auto_plain')
    if bundle.kind == 'invalid':
        return UploadPlan(mode='skip', plain=None, synced=None, reason='invalid_lyrics')
    return UploadPlan(mode='skip', plain=None, synced=None, reason='empty_lyrics')


def move_files_after_processing(config: UpConfig, item: InputItem, bundle: LyricsBundle) -> None:
    audio_target_path = None
    if item.source_kind == 'audio' and config.done_tracks_dir and item.original_meta.path is not None:
        moved = move_with_dedup(item.original_meta.path, config.done_tracks_dir)
        if moved:
            audio_target_path = moved
            log_info(f'moved audio to {moved}')
    lrc_path = bundle.synced_path or bundle.plain_path
    if lrc_path:
        target_dir = lrc_path.parent
        if config.done_lrc_dir:
            target_dir = config.done_lrc_dir
        elif config.follow_track:
            if item.source_kind == 'audio' and audio_target_path is not None:
                target_dir = audio_target_path.parent
            elif item.original_meta.path is not None:
                target_dir = item.original_meta.path.parent
        new_name = None
        if config.rename_lrc:
            if item.source_kind == 'audio' and audio_target_path is not None:
                new_name = audio_target_path.stem
            elif item.original_meta.path is not None:
                new_name = item.original_meta.path.stem
        moved_lrc = move_with_dedup(lrc_path, target_dir, new_name=new_name)
        if moved_lrc:
            log_info(f'moved lyrics file to {moved_lrc}')
    cleanup_empty_dirs(config.tracks_dir)
    if config.lyrics_dir:
        cleanup_empty_dirs(config.lyrics_dir)
    if config.plain_dir:
        cleanup_empty_dirs(config.plain_dir)
    if config.synced_dir:
        cleanup_empty_dirs(config.synced_dir)


def _should_use_lookup(config: UpConfig, interaction: Interaction, result: LookupResult, kind: str) -> bool:
    if not result.record:
        return False
    if result.duration_ok or config.ignore_duration_mismatch:
        return interaction.confirm(f'Use {kind} lyrics directly?', default=False)
    return interaction.confirm(
        f'{kind.capitalize()} lyrics duration differs by {result.duration_diff}s. Use them anyway?',
        default=False,
    )


def _upload_record(client: ApiClient, meta: TrackMeta, record: LyricsRecord, config: UpConfig) -> bool:
    bundle = bundle_from_record(record, mode=config.lyrics_mode, allow_derived_plain=config.allow_derived_plain)
    plan = build_upload_plan(bundle, mode=config.lyrics_mode, allow_derived_plain=config.allow_derived_plain)
    if plan.mode == 'instrumental':
        return client.upload_instrumental(meta)
    if plan.mode == 'skip':
        log_warn(f'remote lyrics skipped: {plan.reason}')
        return False
    return client.upload_lyrics(meta, plan.plain or '', plan.synced or '')


def _preview_bundle(prefix: str, bundle: LyricsBundle, max_lines: int) -> None:
    preview(f'{prefix} plainLyrics', bundle.plain, max_lines)
    preview(f'{prefix} syncedLyrics', bundle.synced, max_lines)
    if bundle.warnings:
        log_warn(f'{prefix} warnings: {", ".join(bundle.warnings)}')


def process_item(config: UpConfig, client: ApiClient, item: InputItem, interaction: Interaction) -> None:
    log_info(f'processing {item.label}')

    cached = client.get_cached(item.api_meta)
    if cached.record:
        remote_bundle = bundle_from_record(cached.record, mode=config.lyrics_mode, allow_derived_plain=config.allow_derived_plain)
        _preview_bundle('cached', remote_bundle, config.common.preview_lines)
        if _should_use_lookup(config, interaction, cached, 'cached'):
            move_files_after_processing(config, item, LyricsBundle.empty())
            log_info('accepted cache record; skipped upload')
            return

    external = client.get_external(item.api_meta)
    if external.record:
        remote_bundle = bundle_from_record(external.record, mode=config.lyrics_mode, allow_derived_plain=config.allow_derived_plain)
        _preview_bundle('external', remote_bundle, config.common.preview_lines)
        if _should_use_lookup(config, interaction, external, 'external'):
            if _upload_record(client, item.api_meta, external.record, config):
                log_info('uploaded external lyrics')
                move_files_after_processing(config, item, LyricsBundle.empty())
                return
            log_warn('external upload failed; continuing with local flow')

    local_bundle, plain_candidates, synced_candidates = resolve_local_bundle(item, config, interaction)
    if plain_candidates:
        log_info('plain candidates: ' + ', '.join(str(path) for path in plain_candidates))
    if synced_candidates:
        log_info('synced candidates: ' + ', '.join(str(path) for path in synced_candidates))
    _preview_bundle('local', local_bundle, config.common.preview_lines)
    plan = build_upload_plan(local_bundle, mode=config.lyrics_mode, allow_derived_plain=config.allow_derived_plain)
    if plan.mode == 'skip':
        log_warn(f'skipping upload for {item.label}: {plan.reason}')
        return
    if plan.mode == 'instrumental':
        if interaction.confirm('Upload as instrumental?', default=False) and client.upload_instrumental(item.api_meta):
            move_files_after_processing(config, item, local_bundle)
        return
    if interaction.confirm(f'Upload local lyrics using strategy {config.lyrics_mode}?', default=False):
        if client.upload_lyrics(item.api_meta, plan.plain or '', plan.synced or ''):
            log_info('upload completed')
            move_files_after_processing(config, item, local_bundle)
        else:
            log_error('upload failed')


def run_up(config: UpConfig) -> int:
    interaction = Interaction(interactive=config.common.interactive, assume_yes=config.common.assume_yes)
    client = ApiClient(config.common)
    items = discover_inputs(config.tracks_dir)
    if not items:
        log_warn('no supported audio or YAML files found')
        return 0
    for item in items:
        process_item(config, client, item, interaction)
    return 0
