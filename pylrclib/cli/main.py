from __future__ import annotations

import argparse
import sys

from .. import __version__
from ..commands import cleanse, doctor, down, inspect, search, up
from ..exceptions import CLIUsageError
from ..i18n import setup_i18n
from ..logging_utils import log_error
from .helptext import RichHelpFormatter, with_default


def _detect_lang(argv: list[str]) -> str:
    for index, value in enumerate(argv):
        if value in {"--lang", "--language"} and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith("--lang="):
            return value.split("=", 1)[1]
        if value.startswith("--language="):
            return value.split("=", 1)[1]
    return "auto"


def build_parser(lang: str) -> argparse.ArgumentParser:
    setup_i18n(lang)
    parser = argparse.ArgumentParser(
        prog="pylrclib",
        description=(
            "Command line tools for uploading, downloading, searching, inspecting, and cleansing lyrics around LRCLIB."
        ),
        epilog=(
            "Examples:\n"
            "  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n"
            "  pylrclib down --artist \"Aimer\" --title \"Ref:rain\" --save-mode both\n"
            "  pylrclib search --query \"artist title\"\n"
            "  pylrclib cleanse ./lyrics --write"
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "--lang",
        "--language",
        default=lang,
        choices=["auto", "en_US", "zh_CN"],
        help=with_default(
            "Interface language for command output and prompts.",
            "auto",
        ),
    )
    parser.add_argument("--version", action="version", version=f"pylrclib {__version__}")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="subcommands",
        metavar="COMMAND",
        description="Choose one of the commands below.",
    )
    up.add_parser(subparsers)
    down.add_parser(subparsers)
    search.add_parser(subparsers)
    cleanse.add_parser(subparsers)
    inspect.add_parser(subparsers)
    doctor.add_parser(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    detected_lang = _detect_lang(argv)
    parser = build_parser(detected_lang)
    args = parser.parse_args(argv)
    lang = setup_i18n(args.lang)
    try:
        return int(args.command_handler(args, lang) or 0)
    except CLIUsageError as exc:
        log_error(str(exc))
        return 2
    except KeyboardInterrupt:
        log_error("interrupted by user")
        return 130
