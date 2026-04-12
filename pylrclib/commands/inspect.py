from __future__ import annotations

from argparse import ArgumentParser, Namespace

from ..config import PREVIEW_LINES_DEFAULT, UNSET, resolve_int
from ..lyrics import load_local_lyrics_bundle
from ..workflows.up import discover_inputs
from .up import _build_config


def add_parser(subparsers) -> ArgumentParser:
    parser = subparsers.add_parser("inspect", help="inspect inputs and local lyrics matches without uploading")
    parser.add_argument("--tracks", default=UNSET)
    parser.add_argument("--lyrics-dir", default=UNSET)
    parser.add_argument("--plain-dir", default=UNSET)
    parser.add_argument("--synced-dir", default=UNSET)
    parser.add_argument("--lyrics-mode", default="auto", choices=["auto", "plain", "synced", "mixed", "instrumental"])
    parser.add_argument("--preview-lines", default=UNSET)
    parser.add_argument("--show-all-candidates", action="store_true")
    parser.set_defaults(command_handler=run)
    return parser


def run(args: Namespace, lang: str) -> int:
    args.done_tracks = UNSET
    args.done_lrc = UNSET
    args.follow = False
    args.rename = False
    args.cleanse = False
    args.cleanse_write = False
    args.allow_non_lrc = False
    args.ignore_duration_mismatch = False
    args.default = None
    args.match = False
    args.max_retries = UNSET
    args.user_agent = UNSET
    args.api_base = UNSET
    args.yes = False
    args.non_interactive = True
    args.allow_derived_plain = True
    config = _build_config(args, lang)
    config.common.preview_lines = resolve_int(args.preview_lines, "PYLRCLIB_PREVIEW_LINES", PREVIEW_LINES_DEFAULT)
    items = discover_inputs(config)
    print(f"Found {len(items)} item(s).")
    for item in items:
        print(item.label)
        bundle, plain_candidates, synced_candidates = load_local_lyrics_bundle(item, config)
        if args.show_all_candidates:
            for candidate in plain_candidates:
                print(f"  plain candidate: {candidate}")
            for candidate in synced_candidates:
                print(f"  synced candidate: {candidate}")
        else:
            print(f"  plain: {plain_candidates[0] if plain_candidates else '[none]'}")
            print(f"  synced: {synced_candidates[0] if synced_candidates else '[none]'}")
        print(f"  resolved_kind={bundle.kind} warnings={bundle.warnings}")
        if bundle.plain:
            print("--- inspect plainLyrics ---")
            for line in bundle.plain.splitlines()[:config.common.preview_lines]:
                print(line)
        if bundle.synced:
            print("--- inspect syncedLyrics ---")
            for line in bundle.synced.splitlines()[:config.common.preview_lines]:
                print(line)
    return 0
