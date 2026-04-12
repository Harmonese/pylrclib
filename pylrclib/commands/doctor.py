from __future__ import annotations

from argparse import ArgumentParser, Namespace

from ..config import SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_YAML_EXTENSIONS, SUPPORTED_PLAIN_EXTENSIONS, SUPPORTED_SYNCED_EXTENSIONS, UNSET
from ..logging_utils import log_info, log_warn
from ..discovery import discover_inputs
from .up import _build_config


def add_parser(subparsers) -> ArgumentParser:
    parser = subparsers.add_parser("doctor", help="diagnose the current workspace and resolved configuration")
    parser.add_argument("--tracks", default=UNSET)
    parser.add_argument("--lyrics-dir", default=UNSET)
    parser.add_argument("--plain-dir", default=UNSET)
    parser.add_argument("--synced-dir", default=UNSET)
    parser.add_argument("--done-tracks", default=UNSET)
    parser.add_argument("--done-lrc", default=UNSET)
    parser.add_argument("-f", "--follow", action="store_true")
    parser.add_argument("-r", "--rename", action="store_true")
    parser.add_argument("-c", "--cleanse", action="store_true")
    parser.add_argument("--lyrics-mode", default="auto", choices=["auto", "plain", "synced", "mixed", "instrumental"])
    parser.add_argument("-d", "--default", nargs=2, metavar=("TRACKS_DIR", "LYRICS_DIR"))
    parser.add_argument("-m", "--match", action="store_true")
    parser.add_argument("--preview-lines", default=UNSET)
    parser.add_argument("--max-retries", default=UNSET)
    parser.add_argument("--user-agent", default=UNSET)
    parser.add_argument("--api-base", default=UNSET)
    parser.set_defaults(command_handler=run)
    return parser


def run(args: Namespace, lang: str) -> int:
    args.cleanse_write = False
    args.allow_non_lrc = False
    args.ignore_duration_mismatch = False
    args.yes = False
    args.non_interactive = True
    args.allow_derived_plain = True
    config = _build_config(args, lang)
    print("Resolved configuration:")
    print(f"  tracks_dir={config.tracks_dir}")
    print(f"  lyrics_dir={config.lyrics_dir}")
    print(f"  plain_dir={config.plain_dir}")
    print(f"  synced_dir={config.synced_dir}")
    print(f"  done_tracks_dir={config.done_tracks_dir}")
    print(f"  done_lrc_dir={config.done_lrc_dir}")
    print(f"  follow_track={config.follow_track}")
    print(f"  rename_lrc={config.rename_lrc}")
    print(f"  cleanse={config.cleanse}")
    print(f"  lyrics_mode={config.lyrics_mode}")
    print(f"  mode={config.mode}")
    print(f"  api_base={config.common.lrclib_base}")
    print(f"  max_retries={config.common.max_http_retries}")

    errors = 0
    if not config.tracks_dir.exists():
        log_warn(f"tracks_dir does not exist: {config.tracks_dir}")
        errors += 1
    if config.follow_track and config.done_lrc_dir:
        log_warn("follow_track and done_lrc_dir should not be combined")
        errors += 1

    audio_count = 0
    yaml_count = 0
    plain_count = 0
    synced_count = 0
    if config.tracks_dir.exists():
        for path in config.tracks_dir.rglob("*"):
            if path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                audio_count += 1
            elif path.suffix.lower() in SUPPORTED_YAML_EXTENSIONS:
                yaml_count += 1
    for directory, exts, counter_name in [
        (config.lyrics_dir, SUPPORTED_PLAIN_EXTENSIONS, "plain"),
        (config.plain_dir, SUPPORTED_PLAIN_EXTENSIONS, "plain"),
        (config.lyrics_dir, SUPPORTED_SYNCED_EXTENSIONS, "synced"),
        (config.synced_dir, SUPPORTED_SYNCED_EXTENSIONS, "synced"),
    ]:
        if directory and directory.exists():
            count = sum(1 for path in directory.rglob("*") if path.suffix.lower() in exts)
            if counter_name == "plain":
                plain_count += count
            else:
                synced_count += count
    items = discover_inputs(config.tracks_dir)
    print(f"Found audio={audio_count}, yaml={yaml_count}, plain={plain_count}, synced={synced_count}, valid_inputs={len(items)}")
    if errors:
        return 1
    log_info("doctor finished without fatal issues")
    return 0
