from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..config import PREVIEW_LINES_DEFAULT, UNSET, resolve_int
from ..logging_utils import log_info, log_warn
from ..lrc import cleanse_lrc_file


def add_parser(subparsers) -> ArgumentParser:
    parser = subparsers.add_parser("cleanse", help="cleanse LRC files without uploading")
    parser.add_argument("paths", nargs="*", default=[])
    parser.add_argument("--lrc-dir", default=UNSET)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--preview-lines", default=UNSET)
    parser.set_defaults(command_handler=run)
    return parser


def _collect_paths(args: Namespace) -> list[Path]:
    if args.paths:
        raw_paths = [Path(value).expanduser().resolve() for value in args.paths]
    elif args.lrc_dir is not UNSET:
        raw_paths = [Path(str(args.lrc_dir)).expanduser().resolve()]
    else:
        raw_paths = [Path.cwd().resolve()]
    files: list[Path] = []
    for path in raw_paths:
        if path.is_file() and path.suffix.lower() == ".lrc":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.lrc")))
    return files


def run(args: Namespace, lang: str) -> int:
    del lang
    preview_lines = resolve_int(args.preview_lines, "PYLRCLIB_PREVIEW_LINES", PREVIEW_LINES_DEFAULT)
    files = _collect_paths(args)
    if not files:
        log_warn("no LRC files found")
        return 0
    stats = {"updated": 0, "unchanged": 0, "invalid": 0, "failed": 0}
    for path in files:
        result = cleanse_lrc_file(path, write=args.write)
        stats[result.status] = stats.get(result.status, 0) + 1
        log_info(f"{path}: {result.status}")
        if result.cleaned_text:
            lines = result.cleaned_text.splitlines()
            for line in lines[:preview_lines]:
                print(line)
            if len(lines) > preview_lines:
                print(f"... ({len(lines)} lines total)")
    log_info("summary: " + ", ".join(f"{key}={value}" for key, value in sorted(stats.items())))
    return 0
