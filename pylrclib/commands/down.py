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
    DownConfig,
    resolve_int,
    resolve_optional_int,
    resolve_optional_str,
    resolve_path,
    resolve_str,
)
from ..exceptions import CLIUsageError
from ..i18n import get_text
from ..workflows.down import run_down


SAVE_MODES = ['auto', 'plain', 'synced', 'both']
NAMING_MODES = ['auto', 'track-basename', 'artist-title']


def add_parser(subparsers) -> ArgumentParser:
    net = common_network_help()
    parser = subparsers.add_parser(
        'down',
        help=get_text('cmd.down.help'),
        description=get_text('cmd.down.description'),
        epilog=get_text('cmd.down.epilog'),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument('--tracks', default=UNSET, help=with_default(get_text('cmd.down.arg.tracks'), get_text('default.disabled')))
    parser.add_argument('--artist', default=UNSET, help=with_default(get_text('cmd.down.arg.artist'), get_text('default.unset')))
    parser.add_argument('--title', default=UNSET, help=with_default(get_text('cmd.down.arg.title'), get_text('default.unset')))
    parser.add_argument('--album', default=UNSET, help=with_default(get_text('cmd.down.arg.album'), get_text('default.unset')))
    parser.add_argument('--duration', default=UNSET, help=with_default(get_text('cmd.down.arg.duration'), get_text('default.unset')))
    parser.add_argument('--lrclib-id', default=UNSET, help=with_default(get_text('cmd.down.arg.lrclib_id'), get_text('default.disabled')))
    parser.add_argument('--output-dir', default=UNSET, help=with_default(get_text('cmd.down.arg.output_dir'), get_text('default.cwd_output')))
    parser.add_argument('--plain-dir', default=UNSET, help=with_default(get_text('cmd.down.arg.plain_dir'), get_text('default.same_output_dir')))
    parser.add_argument('--synced-dir', default=UNSET, help=with_default(get_text('cmd.down.arg.synced_dir'), get_text('default.same_output_dir')))
    parser.add_argument('--save-mode', default='auto', choices=SAVE_MODES, help=with_default(get_text('cmd.down.arg.save_mode'), get_text('default.auto')))
    parser.add_argument('--naming', default='auto', choices=NAMING_MODES, help=with_default(get_text('cmd.down.arg.naming'), get_text('default.auto')))
    parser.add_argument('--skip-existing', action='store_true', help=with_default(get_text('cmd.down.arg.skip_existing'), get_text('default.disabled')))
    parser.add_argument('--overwrite', action='store_true', help=with_default(get_text('cmd.down.arg.overwrite'), get_text('default.disabled')))
    parser.add_argument('--allow-derived-plain', action='store_true', default=True, help=with_default(get_text('cmd.down.arg.allow_derived_plain'), get_text('default.enabled')))
    parser.add_argument('--no-derived-plain', dest='allow_derived_plain', action='store_false', help=with_default(get_text('cmd.down.arg.no_derived_plain'), get_text('default.disabled')))
    parser.add_argument('--preview-lines', default=UNSET, help=net['preview_lines'])
    parser.add_argument('--max-retries', default=UNSET, help=net['max_retries'])
    parser.add_argument('--user-agent', default=UNSET, help=net['user_agent'])
    parser.add_argument('--api-base', default=UNSET, help=net['api_base'])
    parser.add_argument('--yes', action='store_true', help=net['yes'])
    parser.add_argument('--non-interactive', action='store_true', help=net['non_interactive'])
    parser.set_defaults(command_handler=run)
    return parser


def _validate(args: Namespace) -> None:
    manual = args.artist is not UNSET or args.title is not UNSET
    by_id = args.lrclib_id is not UNSET
    if by_id and (manual or args.tracks is not UNSET):
        raise CLIUsageError(get_text('validate.lrclib_id_tracks_conflict'))
    if manual and args.tracks is not UNSET:
        raise CLIUsageError(get_text('validate.tracks_manual_conflict'))
    if manual and (args.artist is UNSET or args.title is UNSET):
        raise CLIUsageError(get_text('validate.manual_requires_artist_title'))
    if not by_id and not manual and args.tracks is UNSET:
        raise CLIUsageError(get_text('validate.down_missing_input'))
    if args.skip_existing and args.overwrite:
        raise CLIUsageError(get_text('validate.skip_overwrite_conflict'))


def _build_config(args: Namespace, lang: str) -> DownConfig:
    _validate(args)
    cwd = Path.cwd().resolve()
    tracks_dir = resolve_path(args.tracks, 'PYLRCLIB_TRACKS_DIR') if args.tracks is not UNSET else None
    output_dir = resolve_path(args.output_dir, 'PYLRCLIB_OUTPUT_DIR', cwd) or cwd
    plain_dir = resolve_path(args.plain_dir, 'PYLRCLIB_PLAIN_DIR')
    synced_dir = resolve_path(args.synced_dir, 'PYLRCLIB_SYNCED_DIR')
    common = CommonOptions(
        lang=lang,
        preview_lines=resolve_int(args.preview_lines, 'PYLRCLIB_PREVIEW_LINES', PREVIEW_LINES_DEFAULT),
        max_http_retries=resolve_int(args.max_retries, 'PYLRCLIB_MAX_HTTP_RETRIES', MAX_HTTP_RETRIES_DEFAULT),
        user_agent=resolve_str(args.user_agent, 'PYLRCLIB_USER_AGENT', DEFAULT_USER_AGENT),
        lrclib_base=resolve_str(args.api_base, 'PYLRCLIB_API_BASE', LRCLIB_BASE),
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
        artist=resolve_optional_str(args.artist, 'PYLRCLIB_ARTIST'),
        track=resolve_optional_str(args.title, 'PYLRCLIB_TITLE'),
        album=resolve_optional_str(args.album, 'PYLRCLIB_ALBUM'),
        duration=resolve_optional_int(args.duration, 'PYLRCLIB_DURATION'),
        lrclib_id=resolve_optional_int(args.lrclib_id, 'PYLRCLIB_LRCLIB_ID'),
        allow_derived_plain=args.allow_derived_plain,
        common=common,
    )


def run(args: Namespace, lang: str) -> int:
    config = _build_config(args, lang)
    return run_down(config)
