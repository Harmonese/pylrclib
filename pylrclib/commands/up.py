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
from ..workflows.up import run_up


LYRICS_MODES = ["auto", "plain", "synced", "mixed", "instrumental"]


def add_parser(subparsers) -> ArgumentParser:
    net = common_network_help()
    parser = subparsers.add_parser(
        "up",
        help="upload local lyrics to LRCLIB",
        description=(
            "Run the full upload workflow. The command scans audio or YAML metadata, resolves local plain and synced lyrics, "
            "checks LRCLIB for existing records, and optionally publishes new lyrics."
        ),
        epilog=(
            "Examples:\n"
            "  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n"
            "  pylrclib up --tracks ./tracks --plain-dir ./plain --synced-dir ./lrc --lyrics-mode mixed\n"
            "  pylrclib up -d ./tracks ./lyrics"
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "--tracks",
        default=UNSET,
        help=with_default(
            "Directory containing input audio files or YAML metadata files to upload.",
            "current working directory, or $PYLRCLIB_TRACKS_DIR when set",
        ),
    )
    parser.add_argument(
        "--lyrics-dir",
        default=UNSET,
        help=with_default(
            "Shared lyrics directory that may contain both plain text lyrics and synced .lrc files.",
            "current working directory when neither --plain-dir nor --synced-dir is given; otherwise unset",
        ),
    )
    parser.add_argument(
        "--plain-dir",
        default=UNSET,
        help=with_default(
            "Directory to search for plain text lyrics such as .txt files.",
            "same as --lyrics-dir, or current working directory when no lyric directories are provided",
        ),
    )
    parser.add_argument(
        "--synced-dir",
        default=UNSET,
        help=with_default(
            "Directory to search for synced lyrics such as .lrc files.",
            "same as --lyrics-dir, or current working directory when no lyric directories are provided",
        ),
    )
    parser.add_argument(
        "--done-tracks",
        default=UNSET,
        help=with_default(
            "Directory where successfully processed track files are moved after upload.",
            "disabled",
        ),
    )
    parser.add_argument(
        "--done-lrc",
        default=UNSET,
        help=with_default(
            "Directory where processed lyric files are moved after upload.",
            "disabled",
        ),
    )
    parser.add_argument(
        "-f", "--follow", action="store_true",
        help=with_default(
            "Move matched lyric files to follow the track destination instead of using --done-lrc.",
            "disabled",
        ),
    )
    parser.add_argument(
        "-r", "--rename", action="store_true",
        help=with_default(
            "Rename matched lyric files to use the same base name as the track file when moving.",
            "disabled",
        ),
    )
    parser.add_argument(
        "-c", "--cleanse", action="store_true",
        help=with_default(
            "Cleanse synced .lrc content before upload so invalid or noisy lines are normalized.",
            "disabled",
        ),
    )
    parser.add_argument(
        "--cleanse-write", action="store_true",
        help=with_default(
            "Write cleansed synced lyrics back to disk. Requires --cleanse.",
            "disabled",
        ),
    )
    parser.add_argument(
        "--allow-non-lrc", action="store_true",
        help=with_default(
            "Allow manually selected synced lyric files that do not use the .lrc extension.",
            "disabled",
        ),
    )
    parser.add_argument(
        "--ignore-duration-mismatch", action="store_true",
        help=with_default(
            "Do not warn or stop when LRCLIB returns a record whose duration differs from the local track.",
            "disabled",
        ),
    )
    parser.add_argument(
        "--lyrics-mode", default="auto", choices=LYRICS_MODES,
        help=with_default(
            "Upload strategy: auto chooses the best available lyrics, plain uploads only plain text, synced uploads only LRC, mixed requires both, instrumental publishes instrumental metadata.",
            "auto",
        ),
    )
    parser.add_argument(
        "--allow-derived-plain", action="store_true", default=True,
        help=with_default(
            "Allow plain lyrics to be derived from synced LRC when no separate plain text file exists.",
            "enabled",
        ),
    )
    parser.add_argument(
        "--no-derived-plain", dest="allow_derived_plain", action="store_false",
        help=with_default(
            "Disable deriving plain lyrics from synced lyrics.",
            "disabled",
        ),
    )
    parser.add_argument(
        "-d", "--default", nargs=2, metavar=("TRACKS_DIR", "LYRICS_DIR"),
        help=with_default(
            "Shortcut mode: equivalent to setting tracks and one shared lyric directory, then enabling follow, rename, and cleanse together.",
            "disabled",
        ),
    )
    parser.add_argument(
        "-m", "--match", action="store_true",
        help=with_default(
            "Match mode: enable follow, rename, and cleanse while still using individually resolved directories.",
            "disabled",
        ),
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
        raise CLIUsageError("--follow and --done-lrc cannot be used together")
    if args.default and args.match:
        raise CLIUsageError("-d/--default and -m/--match cannot be used together")
    if args.cleanse_write and not args.cleanse:
        raise CLIUsageError("--cleanse-write requires --cleanse")
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
            raise CLIUsageError("-d/--default cannot be combined with: " + ", ".join(active))


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
