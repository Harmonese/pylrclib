from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..cli.helptext import RichHelpFormatter, common_network_help, with_default
from ..config import (
    DEFAULT_USER_AGENT,
    LRCLIB_BASE,
    MAX_HTTP_RETRIES_DEFAULT,
    PREVIEW_LINES_DEFAULT,
    UNSET,
    CommonOptions,
    UpConfig,
    resolve_int,
    resolve_path,
    resolve_str,
)
from ..exceptions import CLIUsageError
from ..i18n import get_text
from ..workflows.up import run_up


LYRICS_MODES = ["auto", "plain", "synced", "mixed", "instrumental"]


def add_parser(subparsers) -> ArgumentParser:
    net = common_network_help()
    parser = subparsers.add_parser(
        "up",
        help=get_text("cmd.up.help"),
        description=get_text("cmd.up.description"),
        epilog=get_text("cmd.up.epilog"),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "--tracks",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.tracks"), get_text("default.cwd_tracks")),
    )
    parser.add_argument(
        "--lyrics-dir",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.lyrics_dir"), get_text("default.cwd_lyrics")),
    )
    parser.add_argument(
        "--plain-dir",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.plain_dir"), get_text("default.same_lyrics")),
    )
    parser.add_argument(
        "--synced-dir",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.synced_dir"), get_text("default.same_lyrics")),
    )
    parser.add_argument(
        "--done-tracks",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.done_tracks"), get_text("default.disabled")),
    )
    parser.add_argument(
        "--done-lrc",
        default=UNSET,
        help=with_default(get_text("cmd.up.arg.done_lrc"), get_text("default.disabled")),
    )
    parser.add_argument(
        "-f", "--follow", action="store_true",
        help=with_default(get_text("cmd.up.arg.follow"), get_text("default.disabled")),
    )
    parser.add_argument(
        "-r", "--rename", action="store_true",
        help=with_default(get_text("cmd.up.arg.rename"), get_text("default.disabled")),
    )
    parser.add_argument(
        "-c", "--cleanse", action="store_true",
        help=with_default(get_text("cmd.up.arg.cleanse"), get_text("default.disabled")),
    )
    parser.add_argument(
        "--cleanse-write", action="store_true",
        help=with_default(get_text("cmd.up.arg.cleanse_write"), get_text("default.disabled")),
    )
    parser.add_argument(
        "--allow-non-lrc", action="store_true",
        help=with_default(get_text("cmd.up.arg.allow_non_lrc"), get_text("default.disabled")),
    )
    parser.add_argument(
        "--ignore-duration-mismatch", action="store_true",
        help=with_default(get_text("cmd.up.arg.ignore_duration_mismatch"), get_text("default.disabled")),
    )
    parser.add_argument(
        "--lyrics-mode", default="auto", choices=LYRICS_MODES,
        help=with_default(get_text("cmd.up.arg.lyrics_mode"), get_text("default.auto")),
    )
    parser.add_argument(
        "--allow-derived-plain", action="store_true", default=True,
        help=with_default(get_text("cmd.up.arg.allow_derived_plain"), get_text("default.enabled")),
    )
    parser.add_argument(
        "--no-derived-plain", dest="allow_derived_plain", action="store_false",
        help=with_default(get_text("cmd.up.arg.no_derived_plain"), get_text("default.disabled")),
    )
    parser.add_argument(
        "-d", "--default", nargs=2, metavar=("TRACKS_DIR", "LYRICS_DIR"),
        help=with_default(get_text("cmd.up.arg.default"), get_text("default.disabled")),
    )
    parser.add_argument(
        "-m", "--match", action="store_true",
        help=with_default(get_text("cmd.up.arg.match"), get_text("default.disabled")),
    )
    parser.add_argument("--preview-lines", default=UNSET, help=net["preview_lines"])
    parser.add_argument("--max-retries", default=UNSET, help=net["max_retries"])
    parser.add_argument("--user-agent", default=UNSET, help=net["user_agent"])
    parser.add_argument("--api-base", default=UNSET, help=net["api_base"])
    parser.add_argument("--yes", action="store_true", help=net["yes"])
    parser.add_argument("--non-interactive", action="store_true", help=net["non_interactive"])
    parser.set_defaults(command_handler=run)
    return parser


def _validate(args: Namespace) -> None:
    if args.follow and args.done_lrc is not UNSET:
        raise CLIUsageError(get_text("validate.follow_done_conflict"))
    if args.default and args.match:
        raise CLIUsageError(get_text("validate.default_match_conflict"))
    if args.cleanse_write and not args.cleanse:
        raise CLIUsageError(get_text("validate.cleanse_write_requires_cleanse"))
    if args.default:
        conflicts = [
            (args.follow, "--follow"),
            (args.rename, "--rename"),
            (args.cleanse, "--cleanse"),
            (args.tracks is not UNSET, "--tracks"),
            (args.lyrics_dir is not UNSET, "--lyrics-dir"),
            (args.plain_dir is not UNSET, "--plain-dir"),
            (args.synced_dir is not UNSET, "--synced-dir"),
            (args.done_tracks is not UNSET, "--done-tracks"),
            (args.done_lrc is not UNSET, "--done-lrc"),
        ]
        active = [name for enabled, name in conflicts if enabled]
        if active:
            raise CLIUsageError(get_text("validate.default_cannot_combine", names=", ".join(active)))


def _build_config(args: Namespace, lang: str) -> UpConfig:
    _validate(args)
    cwd = Path.cwd().resolve()
    if args.default:
        tracks_dir = Path(args.default[0]).expanduser().resolve()
        lyrics_dir = Path(args.default[1]).expanduser().resolve()
        plain_dir = lyrics_dir
        synced_dir = lyrics_dir
        done_tracks_dir = None
        done_lrc_dir = None
        follow_track = True
        rename_lrc = True
        cleanse = True
        mode = "default"
    else:
        tracks_dir = resolve_path(args.tracks, "PYLRCLIB_TRACKS_DIR", cwd)
        lyrics_dir = resolve_path(args.lyrics_dir, "PYLRCLIB_LYRICS_DIR")
        plain_dir = resolve_path(args.plain_dir, "PYLRCLIB_PLAIN_DIR")
        synced_dir = resolve_path(args.synced_dir, "PYLRCLIB_SYNCED_DIR")
        if lyrics_dir is None and plain_dir is None and synced_dir is None:
            lyrics_dir = cwd
            plain_dir = cwd
            synced_dir = cwd
        else:
            if plain_dir is None:
                plain_dir = lyrics_dir
            if synced_dir is None:
                synced_dir = lyrics_dir
        done_tracks_dir = resolve_path(args.done_tracks, "PYLRCLIB_DONE_TRACKS_DIR")
        done_lrc_dir = resolve_path(args.done_lrc, "PYLRCLIB_DONE_LRC_DIR")
        follow_track = args.follow or args.match
        rename_lrc = args.rename or args.match
        cleanse = args.cleanse or args.match
        mode = "match" if args.match else "normal"
    common = CommonOptions(
        lang=lang,
        preview_lines=resolve_int(args.preview_lines, "PYLRCLIB_PREVIEW_LINES", PREVIEW_LINES_DEFAULT),
        max_http_retries=resolve_int(args.max_retries, "PYLRCLIB_MAX_HTTP_RETRIES", MAX_HTTP_RETRIES_DEFAULT),
        user_agent=resolve_str(args.user_agent, "PYLRCLIB_USER_AGENT", DEFAULT_USER_AGENT),
        lrclib_base=resolve_str(args.api_base, "PYLRCLIB_API_BASE", LRCLIB_BASE),
        interactive=not (args.non_interactive or args.yes),
        assume_yes=args.yes,
    )
    return UpConfig(
        tracks_dir=tracks_dir,
        lyrics_dir=lyrics_dir,
        plain_dir=plain_dir,
        synced_dir=synced_dir,
        done_tracks_dir=done_tracks_dir,
        done_lrc_dir=done_lrc_dir,
        follow_track=follow_track,
        rename_lrc=rename_lrc,
        cleanse=cleanse,
        cleanse_write=args.cleanse_write,
        allow_non_lrc=args.allow_non_lrc,
        ignore_duration_mismatch=args.ignore_duration_mismatch,
        lyrics_mode=args.lyrics_mode,
        allow_derived_plain=args.allow_derived_plain,
        mode=mode,
        common=common,
    )


def run(args: Namespace, lang: str) -> int:
    config = _build_config(args, lang)
    return run_up(config)
