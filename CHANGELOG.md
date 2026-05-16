# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog and this project uses Semantic Versioning.

## [0.4.7] - 2026-05-16

### Fixed
- LRC parser rejected timestamps with fewer than 2 decimal digits (e.g. `[00:12.5]` or `[00:12]`). The initial timestamp guard now uses the same relaxed regex as the per-line parser.
- `solve_pow` infinite loop when the server returned an unsolvable proof-of-work challenge. Added a 2,000,000 iteration cap that raises `PoWError` instead of hanging forever.
- `parse_retry_after` had no upper bound on the returned delay, so a malformed `Retry-After` header could cause arbitrarily long sleeps. Capped at 60 seconds.
- `resolve_int` and `resolve_optional_int` would crash with `ValueError` when the user passed a non-numeric CLI argument (e.g. `--preview-lines abc`). They now fall back to the default / `None` respectively.
- `doctor` command double-counted lyric files when `lyrics_dir`, `plain_dir`, and `synced_dir` resolved to the same directory.

## [0.4.6] - 2026-05-16

### Changed
- `__version__` now reads from `pyproject.toml` at runtime, making it the single source of truth for the version number.

## [0.4.5] - 2026-05-16

### Added
- Chinese (zh_CN) i18n support for all CLI output: help text, prompts, log messages, preview labels, status strings, validate errors, and argparse built-in strings.
- `--lang` / `--language` flag with `auto`, `en_US`, `zh_CN` options. Auto-detects from `$LANG` environment variable.
- Environment variable `PYLRCLIB_LANG` to override locale without CLI flags.

## [0.4.4] - 2026-04-14

### Fixed
- Fixed PyPI tag

## [0.4.3] - 2026-04-13

### Fixed
- Bugs that causes failure in PyPI distribution

## [0.4.2] - 2026-04-13

### Added
- Verbose `--help` message

## [0.4.1] - 2026-04-13

### Added
- Initial `pylrclib` multi-command rebuild with `up`, `down`, `inspect`, `cleanse`, and `doctor`.
- Unified lyrics model for `plain`, `synced`, `mixed`, and `instrumental` handling.

## [0.4.0] - 2026-04-13

### Added
- Added `pylrclib search` for LRCLIB remote search and record preview.
- Added `down --lrclib-id` to fetch and save a specific LRCLIB record by id.
- Added a shared interaction layer so `up`, `down`, and `search` reuse the same confirmation and selection behavior.
- Added remote search and record-id coverage in tests.

### Changed
- Moved input discovery into a shared module instead of routing `down` through `up` internals.
- Enriched remote lyrics records with LRCLIB id plus track/artist/album metadata.
- Refreshed packaging metadata and README for a GitHub-ready layout.