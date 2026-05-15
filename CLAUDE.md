# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`pylrclib` is a multi-command CLI (published as `pylrclib-cli` on PyPI) for searching, downloading, inspecting, cleansing, and publishing lyrics around the [LRCLIB](https://lrclib.net) API. Entry point: `pylrclib` → `pylrclib.cli.main:main`.

## Build / test / lint

```bash
pip install -e ".[dev]"      # install with dev deps
pytest -q                     # run all tests
pytest -q tests/path/to/test.py::test_name  # run a single test
ruff check .                  # lint
mypy pylrclib                 # type-check
python -m build               # build distribution
```

## Architecture

The code is organized in layers, with strict import direction: CLI commands → workflows → API / lyrics / fs utilities. No layer imports upward.

### Core model: lyrics state machine

Lyrics are modeled as four explicit states: `plain`, `synced`, `mixed`, `instrumental`. This shared model drives every command. The core dataclasses are in `pylrclib/models/`:

- **`LyricsRecord`** (`models/lyrics.py:9`) — parsed LRCLIB API response. Has `plain`, `synced`, `instrumental` fields. Constructed via `from_api()` which normalizes the JSON keys.
- **`LookupResult`** (`models/lyrics.py:66`) — wraps a `LyricsRecord` with duration-match metadata from API lookups.
- **`LyricsBundle`** (`models/lyrics.py:73`) — the resolved local/remote lyric content before upload or save. Has `kind` (one of `plain`/`synced`/`mixed`/`instrumental`/`invalid`/`empty`), `plain`, `synced`, `instrumental`, and optional file paths.
- **`TrackMeta`** / **`YamlTrackMeta`** (`models/track.py`) — metadata extracted from audio files (via mutagen) or YAML files. `TrackMeta.from_audio_file()` reads ID3/MP4/Vorbis tags using the `TAG_MAPPINGS` table. `YamlTrackMeta.from_yaml_file()` parses project-specific YAML metadata files.

### CLI layer (`pylrclib/cli/`)

`cli/main.py` builds the top-level `argparse` parser with six subcommands. Each subcommand registers itself via `add_parser(subparsers)` and sets `args.command_handler` to its `run()` function. The chain is:

1. `main()` detects `--lang` from argv, builds the parser, parses args
2. Calls `args.command_handler(args, lang)` — all handlers accept `(Namespace, str) -> int`
3. `CLIUsageError` is caught at the top level for user-friendly argument errors

Six subcommands in `pylrclib/commands/`:
- **`up`** — upload workflow (most complex). Reuses `_build_config()` shared with `doctor` and `inspect`.
- **`down`** — download workflow with three input modes (scan tracks, manual artist/title, LRCLIB id).
- **`search`** — search LRCLIB and preview results (supports `--json` output).
- **`inspect`** — reuse `_build_config` from `up`, show local matching without uploading.
- **`cleanse`** — normalize `.lrc` files (optional `--write`).
- **`doctor`** — reuse `_build_config` from `up`, print resolved config and directory stats.

Each command module uses `UNSET` sentinel (`config.py`) to distinguish "user didn't pass this argument" from `None`/`False`, enabling layered defaults: CLI arg → env var → hardcoded default.

### Configuration (`pylrclib/config.py`)

Central config dataclasses: `CommonOptions` (shared across all commands), `UpConfig`, `DownConfig`. Helper functions (`resolve_path`, `resolve_int`, `resolve_str`, `resolve_optional_*`) implement the CLI→env→default resolution chain using the `UNSET` sentinel. Environment variables follow the `PYLRCLIB_*` naming scheme.

### API layer (`pylrclib/api/`)

- **`client.py`** — `ApiClient` wraps all LRCLIB HTTP calls: `get_cached()`, `get_external()`, `get_by_id()`, `search()`, `upload_lyrics()`, `upload_instrumental()`. All methods use `http_request_json()` from `http.py`.
- **`http.py`** — shared `http_request_json()` with exponential backoff retry, `Retry-After` header parsing, and `404`-as-`None` handling.
- **`retry.py`** — `calculate_backoff()` (exponential with jitter), `parse_retry_after()` (HTTP-date or delta-seconds), retryable status set `{408, 425, 429, 500, 502, 503, 504}`.
- **`publish.py`** — `publish_with_retry()` handles the LRCLIB publish flow: request a challenge token, solve a SHA-256 proof-of-work via `pow.py`, submit with `X-Publish-Token` header. `build_publish_payload()` constructs the JSON body.
- **`pow.py`** — `solve_pow(prefix, target_hex)` brute-forces a SHA-256 nonce.

### LRC parser (`pylrclib/lrc/`)

- **`parser.py`** — Core LRC parsing. `parse_lrc_text()` extracts timed lines using regex `TIMESTAMP_RE` (`\[\d{2}:\d{2}\.\d{2,3}\]`), stripping header tags, credit lines (via `CREDIT_KEYWORDS`), translations (CJK detection), and instrumental markers. Returns `ParsedLRC` with separated `synced` and `plain` text. `cleanse_lrc_file()` is the file-level API with optional `--write`. `normalize_name()` does NFKC normalization plus CJK/fullwidth character folding — used by the matcher for fuzzy filename matching.
- **`matcher.py`** — `find_matching_paths()` matches lyric files to tracks by parsing `Artist - Title` patterns from filenames, normalizing, and comparing. `split_artists()` handles multi-artist separators (`feat.`, `x`, `&`, `和`, `/`, `;`, `、`). `find_yaml_named_candidates()` resolves explicit filenames from YAML metadata.

### Lyrics loader/writer (`pylrclib/lyrics/`)

- **`loader.py`** — `classify_text(path)` classifies any file as `plain`/`synced`/`instrumental`/`invalid` by attempting LRC parse first, then falling back to plain text detection. `collect_candidate_paths()` discovers matching lyric files across configured directories for an input item. `load_local_lyrics_bundle()` resolves the best plain and synced candidate into a `LyricsBundle`. `bundle_from_record()` converts an API `LyricsRecord` into a `LyricsBundle`.
- **`writer.py`** — `write_lyrics_bundle()` writes a bundle to disk under `output_dir`/`plain_dir`/`synced_dir`, respecting `save_mode` (`auto`/`plain`/`synced`/`both`) and `naming` strategy.

### Workflows (`pylrclib/workflows/`)

- **`up.py`** — `run_up()` is the upload orchestrator. For each discovered input item, it: checks LRCLIB cache → checks LRCLIB external → resolves local lyrics → builds an `UploadPlan` via `build_upload_plan()` → publishes → moves files via `move_files_after_processing()`. `build_upload_plan()` is the core decision function mapping `LyricsBundle.kind` + `lyrics_mode` to a concrete upload action.
- **`down.py`** — `run_down()` handles three download scenarios: by ID, by manual artist/title, or by scanning local tracks. Uses `bundle_from_record()` and `write_lyrics_bundle()`.
- **`search.py`** — `run_search()` queries the API and prints formatted or JSON output.

### Filesystem utilities (`pylrclib/fs/`)

- **`mover.py`** — `move_with_dedup()` moves files with automatic `_dupN` suffix on name collisions.
- **`cleaner.py`** — `cleanup_empty_dirs()` removes empty subdirectories recursively.

### Cross-cutting

- **`discovery.py`** — `discover_inputs()` walks a directory tree, creating `InputItem` objects from audio files (`.mp3`, `.m4a`, `.aac`, `.flac`, `.wav`) and YAML files (`.yaml`, `.yml`). Each `InputItem` has both an `original_meta` (source-format metadata) and an `api_meta` (normalized `TrackMeta` for API calls).
- **`interaction.py`** — `Interaction` class for user prompts: `confirm()`, `choose_index()`/`choose_value()`, `missing_lyrics_action()`, `manual_path()`. Respects `--yes` (assume yes) and `--non-interactive` (use safe defaults) flags.
- **`i18n.py`** — Locale detection (`auto` → `$LANG` → `en_US` or `zh_CN`). The framework is in place but `get_text()` is currently a pass-through.
- **`logging_utils.py`** — Simple `log_info`/`log_warn`/`log_error`/`log_debug` functions printing to stdout/stderr with `[LEVEL]` prefix.
- **`exceptions.py`** — `PylrcLibError` base, `PoWError`, `CLIUsageError`.
