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
from ..workflows.down import run_down


SAVE_MODES = ['auto', 'plain', 'synced', 'both']
NAMING_MODES = ['auto', 'track-basename', 'artist-title']


def add_parser(subparsers) -> ArgumentParser:
    net = common_network_help()
    parser = subparsers.add_parser(
        'down',
        help='download lyrics from LRCLIB',
        description=(
            'Download lyrics from LRCLIB either by scanning local tracks, by manual artist/title input, or by a specific LRCLIB record id.'
        ),
        epilog=(
            'Examples:\n'
            '  pylrclib down --tracks ./music --output-dir ./lyrics\n'
            '  pylrclib down --artist "Aimer" --title "Ref:rain" --save-mode both\n'
            '  pylrclib down --lrclib-id 12345 --output-dir ./lyrics'
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument('--tracks', default=UNSET, help=with_default('Directory containing audio or YAML files whose metadata will be used for LRCLIB lookup.', 'disabled'))
    parser.add_argument('--artist', default=UNSET, help=with_default('Manual artist name for a single-track download.', 'unset'))
    parser.add_argument('--title', default=UNSET, help=with_default('Manual track title for a single-track download.', 'unset'))
    parser.add_argument('--album', default=UNSET, help=with_default('Optional album name used to improve matching for manual downloads.', 'unset'))
    parser.add_argument('--duration', default=UNSET, help=with_default('Optional track duration in seconds used to improve matching for manual downloads.', 'unset'))
    parser.add_argument('--lrclib-id', default=UNSET, help=with_default('Fetch one exact LRCLIB record by numeric id instead of searching by metadata.', 'disabled'))
    parser.add_argument('--output-dir', default=UNSET, help=with_default('Base output directory for downloaded lyric files.', 'current working directory, or $PYLRCLIB_OUTPUT_DIR when set'))
    parser.add_argument('--plain-dir', default=UNSET, help=with_default('Directory where plain text lyrics are written. When omitted, plain lyrics go to --output-dir.', 'same as --output-dir'))
    parser.add_argument('--synced-dir', default=UNSET, help=with_default('Directory where synced .lrc lyrics are written. When omitted, synced lyrics go to --output-dir.', 'same as --output-dir'))
    parser.add_argument('--save-mode', default='auto', choices=SAVE_MODES, help=with_default('How to save fetched lyrics: auto chooses the best available output, plain writes only plain text, synced writes only .lrc, both writes both when available.', 'auto'))
    parser.add_argument('--naming', default='auto', choices=NAMING_MODES, help=with_default('Output naming strategy: auto follows local track basenames when possible, track-basename forces local basenames, artist-title uses "Artist - Title".', 'auto'))
    parser.add_argument('--skip-existing', action='store_true', help=with_default('Do not overwrite files that already exist in the output directory.', 'disabled'))
    parser.add_argument('--overwrite', action='store_true', help=with_default('Overwrite files that already exist in the output directory.', 'disabled'))
    parser.add_argument('--allow-derived-plain', action='store_true', default=True, help=with_default('Allow plain lyrics to be generated from synced lyrics when LRCLIB only returns synced lines.', 'enabled'))
    parser.add_argument('--no-derived-plain', dest='allow_derived_plain', action='store_false', help=with_default('Disable generating plain lyrics from synced lyrics.', 'disabled'))
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
        raise CLIUsageError('--lrclib-id cannot be combined with --tracks or manual --artist/--title mode')
    if manual and args.tracks is not UNSET:
        raise CLIUsageError('--tracks cannot be combined with manual --artist/--title mode')
    if manual and (args.artist is UNSET or args.title is UNSET):
        raise CLIUsageError('manual mode requires both --artist and --title')
    if not by_id and not manual and args.tracks is UNSET:
        raise CLIUsageError('either --lrclib-id, --tracks, or both --artist/--title are required')
    if args.skip_existing and args.overwrite:
        raise CLIUsageError('--skip-existing and --overwrite cannot be used together')


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
