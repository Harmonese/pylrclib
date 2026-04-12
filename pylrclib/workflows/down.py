from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..api import ApiClient
from ..config import DownConfig
from ..logging_utils import log_info, log_warn
from ..lyrics import build_output_stem, bundle_from_record, write_lyrics_bundle
from ..models import TrackMeta
from .up import discover_inputs, preview


@dataclass(slots=True)
class DownloadItem:
    meta: TrackMeta
    source_kind: str
    base_path: Path | None = None

    @property
    def label(self) -> str:
        return f"[{self.source_kind}] {self.meta}"


class Interaction:
    def __init__(self, *, interactive: bool, assume_yes: bool) -> None:
        self.interactive = interactive
        self.assume_yes = assume_yes

    def confirm(self, prompt: str, default: bool = False) -> bool:
        if self.assume_yes:
            return True
        if not self.interactive:
            return default
        suffix = "[Y/n]" if default else "[y/N]"
        answer = input(f"{prompt} {suffix}: ").strip().lower()
        if not answer:
            return default
        return answer in {"y", "yes"}


def _discover_items(config: DownConfig) -> list[DownloadItem]:
    if config.tracks_dir is None:
        meta = TrackMeta(path=None, track=config.track or "", artist=config.artist or "", album=config.album or "", duration=config.duration or 0)
        return [DownloadItem(meta=meta, source_kind="manual", base_path=None)]
    from ..commands.up import _build_config as _build_up_config  # type: ignore
    # Build minimal UpConfig-like object for reuse? Instead directly scan via discover_inputs expectations.
    from types import SimpleNamespace
    args = SimpleNamespace(
        tracks=config.tracks_dir,
        lyrics_dir=config.output_dir,
        plain_dir=config.plain_dir,
        synced_dir=config.synced_dir,
        done_tracks=None,
        done_lrc=None,
        follow=False,
        rename=False,
        cleanse=False,
        cleanse_write=False,
        allow_non_lrc=False,
        ignore_duration_mismatch=False,
        lyrics_mode="auto",
        allow_derived_plain=config.allow_derived_plain,
        default=None,
        match=False,
        preview_lines=config.common.preview_lines,
        max_retries=config.common.max_http_retries,
        user_agent=config.common.user_agent,
        api_base=config.common.lrclib_base,
        yes=config.common.assume_yes,
        non_interactive=not config.common.interactive,
    )
    up_config = _build_up_config(args, config.common.lang)
    items = discover_inputs(up_config)
    return [DownloadItem(meta=item.api_meta, source_kind=item.source_kind, base_path=item.original_meta.path) for item in items]


def _default_naming(item: DownloadItem, config: DownConfig) -> str:
    if config.naming == "auto":
        return "track-basename" if item.base_path is not None else "artist-title"
    return config.naming


def run_down(config: DownConfig) -> int:
    interaction = Interaction(interactive=config.common.interactive, assume_yes=config.common.assume_yes)
    client = ApiClient(config.common)
    items = _discover_items(config)
    if not items:
        log_warn("no supported audio or YAML files found")
        return 0
    written_total = 0
    for item in items:
        log_info(f"downloading for {item.label}")
        result = client.get_external(item.meta)
        if not result.record:
            log_warn(f"no lyrics found for {item.label}")
            continue
        bundle = bundle_from_record(result.record, mode="mixed" if config.save_mode == "both" else "auto", allow_derived_plain=config.allow_derived_plain)
        preview("remote plainLyrics", bundle.plain, config.common.preview_lines)
        preview("remote syncedLyrics", bundle.synced, config.common.preview_lines)
        if not result.duration_ok and item.meta.duration > 0:
            if not interaction.confirm(f"Duration differs by {result.duration_diff}s for {item.meta.track}. Save anyway?", default=False):
                continue
        if bundle.instrumental:
            log_info(f"instrumental track reported by LRCLIB: {item.meta.artist} - {item.meta.track}")
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
            log_info(f"wrote {path}")
        written_total += len(written)
    log_info(f"download finished: {written_total} file(s) written")
    return 0
