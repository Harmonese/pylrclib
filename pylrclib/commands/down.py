from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..config import (
    DEFAULT_USER_AGENT,
    LRCLIB_BASE,
    MAX_HTTP_RETRIES_DEFAULT,
    PREVIEW_LINES_DEFAULT,
    UNSET,
    CommonOptions,
    DownConfig,
    resolve_int,
    resolve_optional_int,
    resolve_optional_str,
    resolve_path,
    resolve_str,
)
from ..exceptions import CLIUsageError
from ..workflows.down import run_down


SAVE_MODES = ["auto", "plain", "synced", "both"]
NAMING_MODES = ["auto", "track-basename", "artist-title"]


def add_parser(subparsers) -> ArgumentParser:
    parser = subparsers.add_parser("down", help="download lyrics from LRCLIB")
    parser.add_argument("--tracks", default=UNSET, help="audio/YAML directory to query from")
    parser.add_argument("--artist", default=UNSET)
    parser.add_argument("--title", default=UNSET)
    parser.add_argument("--album", default=UNSET)
    parser.add_argument("--duration", default=UNSET)
    parser.add_argument("--output-dir", default=UNSET)
    parser.add_argument("--plain-dir", default=UNSET)
    parser.add_argument("--synced-dir", default=UNSET)
    parser.add_argument("--save-mode", default="auto", choices=SAVE_MODES)
    parser.add_argument("--naming", default="auto", choices=NAMING_MODES)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--allow-derived-plain", action="store_true", default=True)
    parser.add_argument("--no-derived-plain", dest="allow_derived_plain", action="store_false")
    parser.add_argument("--preview-lines", default=UNSET)
    parser.add_argument("--max-retries", default=UNSET)
    parser.add_argument("--user-agent", default=UNSET)
    parser.add_argument("--api-base", default=UNSET)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    parser.set_defaults(command_handler=run)
    return parser


def _validate(args: Namespace) -> None:
    manual = args.artist is not UNSET or args.title is not UNSET
    if manual and args.tracks is not UNSET:
        raise CLIUsageError("--tracks cannot be combined with manual --artist/--title mode")
    if manual and (args.artist is UNSET or args.title is UNSET):
        raise CLIUsageError("manual mode requires both --artist and --title")
    if not manual and args.tracks is UNSET:
        raise CLIUsageError("either --tracks or both --artist/--title are required")
    if args.skip_existing and args.overwrite:
        raise CLIUsageError("--skip-existing and --overwrite cannot be used together")


def _build_config(args: Namespace, lang: str) -> DownConfig:
    _validate(args)
    cwd = Path.cwd().resolve()
    tracks_dir = resolve_path(args.tracks, "PYLRCLIB_TRACKS_DIR") if args.tracks is not UNSET else None
    output_dir = resolve_path(args.output_dir, "PYLRCLIB_OUTPUT_DIR", cwd) or cwd
    plain_dir = resolve_path(args.plain_dir, "PYLRCLIB_PLAIN_DIR")
    synced_dir = resolve_path(args.synced_dir, "PYLRCLIB_SYNCED_DIR")
    common = CommonOptions(
        lang=lang,
        preview_lines=resolve_int(args.preview_lines, "PYLRCLIB_PREVIEW_LINES", PREVIEW_LINES_DEFAULT),
        max_http_retries=resolve_int(args.max_retries, "PYLRCLIB_MAX_HTTP_RETRIES", MAX_HTTP_RETRIES_DEFAULT),
        user_agent=resolve_str(args.user_agent, "PYLRCLIB_USER_AGENT", DEFAULT_USER_AGENT),
        lrclib_base=resolve_str(args.api_base, "PYLRCLIB_API_BASE", LRCLIB_BASE),
        interactive=not (args.non_interactive or args.yes),
        assume_yes=args.yes,
    )
    return DownConfig(
        tracks_dir=tracks_dir,
        output_dir=output_dir,
        plain_dir=plain_dir,
        synced_dir=synced_dir,
        save_mode=args.save_mode,
        skip_existing=args.skip_existing,
        overwrite=args.overwrite,
        naming=args.naming,
        artist=resolve_optional_str(args.artist, "PYLRCLIB_ARTIST"),
        track=resolve_optional_str(args.title, "PYLRCLIB_TITLE"),
        album=resolve_optional_str(args.album, "PYLRCLIB_ALBUM"),
        duration=resolve_optional_int(args.duration, "PYLRCLIB_DURATION"),
        allow_derived_plain=args.allow_derived_plain,
        common=common,
    )


def run(args: Namespace, lang: str) -> int:
    config = _build_config(args, lang)
    return run_down(config)
