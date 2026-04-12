from __future__ import annotations

from argparse import ArgumentParser, Namespace

from ..config import (
    DEFAULT_USER_AGENT,
    LRCLIB_BASE,
    MAX_HTTP_RETRIES_DEFAULT,
    PREVIEW_LINES_DEFAULT,
    UNSET,
    CommonOptions,
    resolve_int,
    resolve_optional_int,
    resolve_optional_str,
    resolve_str,
)
from ..exceptions import CLIUsageError
from ..workflows.search import run_search


def add_parser(subparsers) -> ArgumentParser:
    parser = subparsers.add_parser('search', help='search LRCLIB and preview remote lyrics records')
    parser.add_argument('--query', default=UNSET)
    parser.add_argument('--title', default=UNSET)
    parser.add_argument('--artist', default=UNSET)
    parser.add_argument('--album', default=UNSET)
    parser.add_argument('--lrclib-id', default=UNSET)
    parser.add_argument('--limit', default=UNSET)
    parser.add_argument('--preview-lines', default=UNSET)
    parser.add_argument('--max-retries', default=UNSET)
    parser.add_argument('--user-agent', default=UNSET)
    parser.add_argument('--api-base', default=UNSET)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--non-interactive', action='store_true')
    parser.set_defaults(command_handler=run)
    return parser


def _validate(args: Namespace) -> None:
    if args.lrclib_id is not UNSET and any(value is not UNSET for value in [args.query, args.title, args.artist, args.album]):
        raise CLIUsageError('--lrclib-id cannot be combined with --query/--title/--artist/--album')
    if args.lrclib_id is UNSET and args.query is UNSET and args.title is UNSET:
        raise CLIUsageError('either --lrclib-id or one of --query/--title is required')


def run(args: Namespace, lang: str) -> int:
    _validate(args)
    options = CommonOptions(
        lang=lang,
        preview_lines=resolve_int(args.preview_lines, 'PYLRCLIB_PREVIEW_LINES', PREVIEW_LINES_DEFAULT),
        max_http_retries=resolve_int(args.max_retries, 'PYLRCLIB_MAX_HTTP_RETRIES', MAX_HTTP_RETRIES_DEFAULT),
        user_agent=resolve_str(args.user_agent, 'PYLRCLIB_USER_AGENT', DEFAULT_USER_AGENT),
        lrclib_base=resolve_str(args.api_base, 'PYLRCLIB_API_BASE', LRCLIB_BASE),
        interactive=not (args.non_interactive or args.yes),
        assume_yes=args.yes,
    )
    return run_search(
        options,
        lrclib_id=resolve_optional_int(args.lrclib_id, 'PYLRCLIB_LRCLIB_ID'),
        query=resolve_optional_str(args.query, 'PYLRCLIB_QUERY'),
        title=resolve_optional_str(args.title, 'PYLRCLIB_TITLE'),
        artist=resolve_optional_str(args.artist, 'PYLRCLIB_ARTIST'),
        album=resolve_optional_str(args.album, 'PYLRCLIB_ALBUM'),
        limit=resolve_optional_int(args.limit, 'PYLRCLIB_LIMIT'),
        as_json=args.json,
    )
