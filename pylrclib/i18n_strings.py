"""Translation tables for pylrclib i18n.

Each locale maps message keys to translated strings.
Keys follow a dotted convention: <module>.<section>.<name>.
"""

STRINGS: dict[str, dict[str, str]] = {
    "en_US": {
        # ── argparse internals ──
        "usage: ": "usage: ",
        "usage": "usage",
        "options": "options",
        "positional arguments": "positional arguments",
        "show this help message and exit": "show this help message and exit",
        "show program's version number and exit": "show program's version number and exit",

        # ── common default value labels ──
        "default.disabled": "disabled",
        "default.enabled": "enabled",
        "default.unset": "unset",
        "default.auto": "auto",
        "default.cwd_tracks": "current working directory, or $PYLRCLIB_TRACKS_DIR when set",
        "default.cwd_lyrics": "current working directory when neither --plain-dir nor --synced-dir is given; otherwise unset",
        "default.same_lyrics": "same as --lyrics-dir, or current working directory when no lyric directories are provided",
        "default.same_lyrics_dir": "same as --lyrics-dir",
        "default.same_output_dir": "same as --output-dir",
        "default.cwd_output": "current working directory, or $PYLRCLIB_OUTPUT_DIR when set",
        "default.cwd_paths": "current working directory when no positional paths and no --lrc-dir are given",
        "default.cwd_lrc_dir": "current working directory when no positional paths are given",
        "default.server_limit": "server default, or $PYLRCLIB_LIMIT when set",
        "default.cwd_when_none": "current working directory when neither --plain-dir nor --synced-dir is given",

        # ── validate error messages ──
        "validate.follow_done_conflict": "--follow and --done-lrc cannot be used together",
        "validate.default_match_conflict": "-d/--default and -m/--match cannot be used together",
        "validate.cleanse_write_requires_cleanse": "--cleanse-write requires --cleanse",
        "validate.default_cannot_combine": "-d/--default cannot be combined with: {names}",
        "validate.lrclib_id_tracks_conflict": "--lrclib-id cannot be combined with --tracks or manual --artist/--title mode",
        "validate.tracks_manual_conflict": "--tracks cannot be combined with manual --artist/--title mode",
        "validate.manual_requires_artist_title": "manual mode requires both --artist and --title",
        "validate.down_missing_input": "either --lrclib-id, --tracks, or both --artist/--title are required",
        "validate.skip_overwrite_conflict": "--skip-existing and --overwrite cannot be used together",
        "validate.lrclib_id_search_conflict": "--lrclib-id cannot be combined with --query/--title/--artist/--album",
        "validate.search_missing_input": "either --lrclib-id or one of --query/--title is required",

        # ── cli/main.py ──
        "cli.description": "Command line tools for uploading, downloading, searching, inspecting, and cleansing lyrics around LRCLIB.",
        "cli.epilog": (
            "Examples:\n"
            '  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n'
            '  pylrclib down --artist "Aimer" --title "Ref:rain" --save-mode both\n'
            '  pylrclib search --query "artist title"\n'
            "  pylrclib cleanse ./lyrics --write"
        ),
        "cli.lang.help": "Interface language for command output and prompts.",
        "cli.subcommands.title": "subcommands",
        "cli.subcommands.description": "Choose one of the commands below.",
        "cli.interrupted": "interrupted by user",

        # ── cli/helptext.py ──
        "cli.default_template": "Default: {default}.",
        "cli.help.preview_lines": "How many lyric lines to preview when showing plain or synced lyrics.",
        "cli.help.max_retries": "Maximum HTTP retry attempts for retryable LRCLIB requests.",
        "cli.help.user_agent": "HTTP User-Agent header sent to LRCLIB.",
        "cli.help.api_base": "Base LRCLIB API URL.",
        "cli.help.yes": "Assume yes for confirmation prompts that would otherwise ask before writing or publishing.",
        "cli.help.non_interactive": "Disable interactive prompts and use safe automatic decisions.",

        # ── commands/up.py ──
        "cmd.up.help": "upload local lyrics to LRCLIB",
        "cmd.up.description": "Run the full upload workflow. The command scans audio or YAML metadata, resolves local plain and synced lyrics, checks LRCLIB for existing records, and optionally publishes new lyrics.",
        "cmd.up.epilog": (
            "Examples:\n"
            "  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n"
            "  pylrclib up --tracks ./tracks --plain-dir ./plain --synced-dir ./lrc --lyrics-mode mixed\n"
            "  pylrclib up -d ./tracks ./lyrics"
        ),
        "cmd.up.arg.tracks": "Directory containing input audio files or YAML metadata files to upload.",
        "cmd.up.arg.lyrics_dir": "Shared lyrics directory that may contain both plain text lyrics and synced .lrc files.",
        "cmd.up.arg.plain_dir": "Directory to search for plain text lyrics such as .txt files.",
        "cmd.up.arg.synced_dir": "Directory to search for synced lyrics such as .lrc files.",
        "cmd.up.arg.done_tracks": "Directory where successfully processed track files are moved after upload.",
        "cmd.up.arg.done_lrc": "Directory where processed lyric files are moved after upload.",
        "cmd.up.arg.follow": "Move matched lyric files to follow the track destination instead of using --done-lrc.",
        "cmd.up.arg.rename": "Rename matched lyric files to use the same base name as the track file when moving.",
        "cmd.up.arg.cleanse": "Cleanse synced .lrc content before upload so invalid or noisy lines are normalized.",
        "cmd.up.arg.cleanse_write": "Write cleansed synced lyrics back to disk. Requires --cleanse.",
        "cmd.up.arg.allow_non_lrc": "Allow manually selected synced lyric files that do not use the .lrc extension.",
        "cmd.up.arg.ignore_duration_mismatch": "Do not warn or stop when LRCLIB returns a record whose duration differs from the local track.",
        "cmd.up.arg.lyrics_mode": "Upload strategy: auto chooses the best available lyrics, plain uploads only plain text, synced uploads only LRC, mixed requires both, instrumental publishes instrumental metadata.",
        "cmd.up.arg.allow_derived_plain": "Allow plain lyrics to be derived from synced LRC when no separate plain text file exists.",
        "cmd.up.arg.no_derived_plain": "Disable deriving plain lyrics from synced lyrics.",
        "cmd.up.arg.default": "Shortcut mode: equivalent to setting tracks and one shared lyric directory, then enabling follow, rename, and cleanse together.",
        "cmd.up.arg.match": "Match mode: enable follow, rename, and cleanse while still using individually resolved directories.",

        # ── commands/down.py ──
        "cmd.down.help": "download lyrics from LRCLIB",
        "cmd.down.description": "Download lyrics from LRCLIB either by scanning local tracks, by manual artist/title input, or by a specific LRCLIB record id.",
        "cmd.down.epilog": (
            "Examples:\n"
            "  pylrclib down --tracks ./music --output-dir ./lyrics\n"
            '  pylrclib down --artist "Aimer" --title "Ref:rain" --save-mode both\n'
            "  pylrclib down --lrclib-id 12345 --output-dir ./lyrics"
        ),
        "cmd.down.arg.tracks": "Directory containing audio or YAML files whose metadata will be used for LRCLIB lookup.",
        "cmd.down.arg.artist": "Manual artist name for a single-track download.",
        "cmd.down.arg.title": "Manual track title for a single-track download.",
        "cmd.down.arg.album": "Optional album name used to improve matching for manual downloads.",
        "cmd.down.arg.duration": "Optional track duration in seconds used to improve matching for manual downloads.",
        "cmd.down.arg.lrclib_id": "Fetch one exact LRCLIB record by numeric id instead of searching by metadata.",
        "cmd.down.arg.output_dir": "Base output directory for downloaded lyric files.",
        "cmd.down.arg.plain_dir": "Directory where plain text lyrics are written. When omitted, plain lyrics go to --output-dir.",
        "cmd.down.arg.synced_dir": "Directory where synced .lrc lyrics are written. When omitted, synced lyrics go to --output-dir.",
        "cmd.down.arg.save_mode": "How to save fetched lyrics: auto chooses the best available output, plain writes only plain text, synced writes only .lrc, both writes both when available.",
        "cmd.down.arg.naming": 'Output naming strategy: auto follows local track basenames when possible, track-basename forces local basenames, artist-title uses "Artist - Title".',
        "cmd.down.arg.skip_existing": "Do not overwrite files that already exist in the output directory.",
        "cmd.down.arg.overwrite": "Overwrite files that already exist in the output directory.",
        "cmd.down.arg.allow_derived_plain": "Allow plain lyrics to be generated from synced lyrics when LRCLIB only returns synced lines.",
        "cmd.down.arg.no_derived_plain": "Disable generating plain lyrics from synced lyrics.",

        # ── commands/search.py ──
        "cmd.search.help": "search LRCLIB and preview remote lyrics records",
        "cmd.search.description": "Search LRCLIB by free-text query or metadata fields, or fetch one exact record by LRCLIB id.",
        "cmd.search.epilog": (
            "Examples:\n"
            '  pylrclib search --query "artist title"\n'
            '  pylrclib search --artist "Aimer" --title "Ref:rain" --album daydream\n'
            "  pylrclib search --lrclib-id 12345 --json"
        ),
        "cmd.search.arg.query": "Free-text query sent to LRCLIB search.",
        "cmd.search.arg.title": "Track title used for structured LRCLIB search.",
        "cmd.search.arg.artist": "Artist name used for structured LRCLIB search.",
        "cmd.search.arg.album": "Album name used for structured LRCLIB search.",
        "cmd.search.arg.lrclib_id": "Fetch one exact LRCLIB record by numeric id.",
        "cmd.search.arg.limit": "Maximum number of LRCLIB search results to display.",
        "cmd.search.arg.json": "Emit raw JSON-like search results instead of the formatted preview view.",

        # ── commands/inspect.py ──
        "cmd.inspect.help": "inspect inputs and local lyrics matches without uploading",
        "cmd.inspect.description": "Inspect local audio or YAML inputs, show matched lyric candidates, and preview the resolved lyrics bundle without uploading anything.",
        "cmd.inspect.epilog": (
            "Examples:\n"
            "  pylrclib inspect --tracks ./music --lyrics-dir ./lyrics\n"
            "  pylrclib inspect --tracks ./music --plain-dir ./plain --synced-dir ./lrc --show-all-candidates"
        ),
        "cmd.inspect.arg.tracks": "Directory containing audio or YAML inputs to inspect.",
        "cmd.inspect.arg.lyrics_dir": "Shared lyrics directory that may contain both plain and synced lyrics.",
        "cmd.inspect.arg.plain_dir": "Directory to search for plain text lyric candidates.",
        "cmd.inspect.arg.synced_dir": "Directory to search for synced lyric candidates.",
        "cmd.inspect.arg.lyrics_mode": "Resolution strategy used to decide which matched lyrics bundle would be chosen.",
        "cmd.inspect.arg.preview_lines": "How many lyric lines to preview for each resolved bundle.",
        "cmd.inspect.arg.show_all_candidates": "Print every matched plain and synced lyric candidate instead of only the top match.",
        "cmd.inspect.found_items": "Found {count} item(s).",

        # ── commands/cleanse.py ──
        "cmd.cleanse.help": "cleanse LRC files without uploading",
        "cmd.cleanse.description": "Cleanse local .lrc files by removing invalid, duplicate, or noisy lines. This command never uploads anything.",
        "cmd.cleanse.epilog": (
            "Examples:\n"
            "  pylrclib cleanse ./lyrics\n"
            "  pylrclib cleanse ./lyrics --write\n"
            "  pylrclib cleanse song.lrc another.lrc"
        ),
        "cmd.cleanse.arg.paths": "One or more .lrc files or directories to cleanse recursively.",
        "cmd.cleanse.arg.lrc_dir": "Directory of .lrc files to cleanse recursively.",
        "cmd.cleanse.arg.write": "Write cleansed output back to the original files. Without this flag, the command previews cleansed results only.",
        "cmd.cleanse.arg.preview_lines": "How many cleansed lines to preview for each processed file.",
        "cmd.cleanse.no_lrc_found": "no LRC files found",
        "cmd.cleanse.summary": "summary: {summary}",

        # ── commands/doctor.py ──
        "cmd.doctor.help": "diagnose the current workspace and resolved configuration",
        "cmd.doctor.description": "Resolve configuration exactly as the upload workflow would, then inspect directories and inputs for common problems.",
        "cmd.doctor.epilog": (
            "Examples:\n"
            "  pylrclib doctor --tracks ./music --lyrics-dir ./lyrics\n"
            "  pylrclib doctor -d ./tracks ./lyrics\n"
            "  pylrclib doctor --tracks ./music --plain-dir ./plain --synced-dir ./lrc"
        ),
        "cmd.doctor.arg.tracks": "Directory containing audio or YAML inputs to validate.",
        "cmd.doctor.arg.lyrics_dir": "Shared lyrics directory that may contain both plain and synced lyric files.",
        "cmd.doctor.arg.plain_dir": "Directory to validate for plain text lyrics.",
        "cmd.doctor.arg.synced_dir": "Directory to validate for synced .lrc lyrics.",
        "cmd.doctor.arg.done_tracks": "Directory where processed tracks would be moved after upload.",
        "cmd.doctor.arg.done_lrc": "Directory where processed lyric files would be moved after upload.",
        "cmd.doctor.arg.follow": "Validate upload mode where lyric files follow track destinations.",
        "cmd.doctor.arg.rename": "Validate upload mode where lyric files are renamed to track basenames.",
        "cmd.doctor.arg.cleanse": "Validate upload mode where synced lyrics are cleansed before upload.",
        "cmd.doctor.arg.lyrics_mode": "Upload strategy to validate against the current workspace.",
        "cmd.doctor.arg.default": "Shortcut mode that validates the default upload preset using one shared lyric directory.",
        "cmd.doctor.arg.match": "Validate the match preset that enables follow, rename, and cleanse together.",
        "cmd.doctor.arg.preview_lines": "How many lyric preview lines upload-like commands would show.",
        "cmd.doctor.arg.max_retries": "Maximum HTTP retry attempts the upload workflow would use.",
        "cmd.doctor.arg.user_agent": "HTTP User-Agent header the upload workflow would send.",
        "cmd.doctor.arg.api_base": "Base LRCLIB API URL the upload workflow would call.",
        "cmd.doctor.resolved_config": "Resolved configuration:",
        "cmd.doctor.found_counts": "Found audio={audio}, yaml={yaml}, plain={plain}, synced={synced}, valid_inputs={items}",
        "cmd.doctor.finished_ok": "doctor finished without fatal issues",
        "cmd.doctor.tracks_not_exist": "tracks_dir does not exist: {path}",
        "cmd.doctor.follow_done_conflict": "follow_track and done_lrc_dir should not be combined",

        # ── interaction.py ──
        "prompt.yes_no_yes_default": "[Y/n]",
        "prompt.yes_no_no_default": "[y/N]",
        "prompt.choose_range": "Choose 1-{max} (or Enter to skip): ",
        "prompt.invalid_input": "Invalid input, try again.",
        "prompt.missing_lyrics_action": "No local lyrics found. Choose [s]kip / [p]lain-file / [y]synced-file / [i]nstrumental / [q]uit: ",
        "prompt.enter_path": "Enter {expected} file path: ",
        "prompt.invalid_file": "Invalid file: {path}",

        # ── workflows/up.py ──
        "wf.up.preview_label": "--- {label} ---",
        "wf.up.empty": "[empty]",
        "wf.up.lines_truncated": "... ({count} lines total)",
        "wf.up.processing": "processing {label}",
        "wf.up.cached_kind": "cached",
        "wf.up.external_kind": "external",
        "wf.up.local_kind": "local",
        "wf.up.accepted_cache": "accepted cache record; skipped upload",
        "wf.up.uploaded_external": "uploaded external lyrics",
        "wf.up.external_failed": "external upload failed; continuing with local flow",
        "wf.up.plain_candidates": "plain candidates: ",
        "wf.up.synced_candidates": "synced candidates: ",
        "wf.up.use_directly": "Use {kind} lyrics directly?",
        "wf.up.duration_differs": "{kind} lyrics duration differs by {diff}s. Use them anyway?",
        "wf.up.skipping": "skipping upload for {label}: {reason}",
        "wf.up.confirm_instrumental": "Upload as instrumental?",
        "wf.up.confirm_upload": "Upload local lyrics using strategy {mode}?",
        "wf.up.upload_completed": "upload completed",
        "wf.up.upload_failed": "upload failed",
        "wf.up.moved_audio": "moved audio to {path}",
        "wf.up.moved_lyrics": "moved lyrics file to {path}",
        "wf.up.remote_skipped": "remote lyrics skipped: {reason}",
        "wf.up.no_inputs": "no supported audio or YAML files found",

        # ── lyrics types for prompts ──
        "lyrics.plain_type": "plain lyrics",
        "lyrics.synced_type": "synced lyrics",

        # ── workflows/down.py ──
        "wf.down.downloading": "downloading for {label}",
        "wf.down.no_lyrics": "no lyrics found for {label}",
        "wf.down.wrote": "wrote {path}",
        "wf.down.finished": "download finished: {count} file(s) written",
        "wf.down.instrumental": "instrumental track reported by LRCLIB: {artist} - {track}",
        "wf.down.duration_differs": "Duration differs by {diff}s for {track}. Save anyway?",
        "wf.down.remote_plain": "remote plainLyrics",
        "wf.down.remote_synced": "remote syncedLyrics",
        "wf.down.no_inputs": "no supported audio or YAML files found",

        # ── workflows/search.py ──
        "wf.search.no_results": "no search results",

        # ── logging_utils.py ──
        "log.info": "INFO",
        "log.warn": "WARN",
        "log.error": "ERROR",
        "log.debug": "DEBUG",

        # ── models/lyrics.py ──
        "model.id_prefix": "#{id} ",
        "model.separator": " - ",
        "model.album_suffix": " [{album}]",
        "model.duration_suffix": " ({duration}s)",
        "model.unknown": "<unknown>",

        # ── lrc/parser.py ──
        "lrc.no_valid_timestamps": "no_valid_timestamps",
        "lrc.read_failed": "read_failed",
        "lrc.empty_after_cleanse": "empty_after_cleanse",
        "lrc.status.invalid": "invalid",
        "lrc.status.unchanged": "unchanged",
        "lrc.status.updated": "updated",
        "lrc.status.failed": "failed",
        "lrc.read_error": "failed to read LRC {path}: {exc}",

        # ── lyrics/loader.py ──
        "lyrics.empty_text": "empty_text",
        "lyrics.instrumental_detected": "instrumental_phrase_detected",
        "lyrics.invalid_plain": "invalid_plain_candidate",
        "lyrics.invalid_synced": "invalid_synced_candidate",
        "lyrics.incomplete_mixed": "incomplete_mixed_lyrics",
        "lyrics.no_plain": "no_plain_lyrics",
        "lyrics.no_synced": "no_synced_lyrics",
        "lyrics.empty_record": "empty_record",

        # ── interaction.py choose labels ──
        "prompt.multiple_plain": "Multiple plain lyric candidates found:",
        "prompt.multiple_synced": "Multiple synced lyric candidates found:",

        # ── cleaner.py / mover.py ──
        "fs.move_failed": "failed to move {src} -> {dst_dir}: {exc}",
        "fs.delete_dir_failed": "failed to delete empty directory {dir}: {exc}",

        # ── api/retry messages ──
        "api.request_error": "{label} request error on attempt {attempt}/{retries}: {exc}; retrying in {delay:.1f}s",
        "api.request_failed": "{label} failed after {attempts} attempts: {exc}",
        "api.invalid_json": "{label} returned invalid JSON: {text}",
        "api.http_fail_final": "{label} failed with HTTP {status} {text}",
        "api.http_fail_retry": "{label} failed with HTTP {status}; retrying in {delay:.1f}s",

        # ── api/publish.py ──
        "api.publish_challenge": "request publish challenge",
        "api.upload_lyrics": "upload lyrics",
        "api.upload_instrumental": "upload instrumental",
        "api.publish_failed": "{label} failed after {attempts} attempts: {exc}",
        "api.publish_http_fail": "{label} failed with HTTP {status}: {text}",
    },
    "zh_CN": {
        # ── argparse internals ──
        "usage: ": "用法：",
        "usage": "用法",
        "options": "选项",
        "positional arguments": "位置参数",
        "show this help message and exit": "显示此帮助信息并退出",
        "show program's version number and exit": "显示程序版本号并退出",

        # ── common default value labels ──
        "default.disabled": "禁用",
        "default.enabled": "启用",
        "default.unset": "未设置",
        "default.auto": "自动",
        "default.cwd_tracks": "当前工作目录，或 $PYLRCLIB_TRACKS_DIR 环境变量（设置时）",
        "default.cwd_lyrics": "当前工作目录（未指定 --plain-dir 和 --synced-dir 时）；否则不设置",
        "default.same_lyrics": "同 --lyrics-dir，或当前工作目录（未提供歌词目录时）",
        "default.same_lyrics_dir": "同 --lyrics-dir",
        "default.same_output_dir": "同 --output-dir",
        "default.cwd_output": "当前工作目录，或 $PYLRCLIB_OUTPUT_DIR 环境变量（设置时）",
        "default.cwd_paths": "当前工作目录（未提供位置参数和 --lrc-dir 时）",
        "default.cwd_lrc_dir": "当前工作目录（未提供位置参数时）",
        "default.server_limit": "服务器默认，或 $PYLRCLIB_LIMIT 环境变量（设置时）",
        "default.cwd_when_none": "当前工作目录（未指定 --plain-dir 和 --synced-dir 时）",

        # ── validate error messages ──
        "validate.follow_done_conflict": "--follow 和 --done-lrc 不能同时使用",
        "validate.default_match_conflict": "-d/--default 和 -m/--match 不能同时使用",
        "validate.cleanse_write_requires_cleanse": "--cleanse-write 需要同时使用 --cleanse",
        "validate.default_cannot_combine": "-d/--default 不能与以下参数同时使用：{names}",
        "validate.lrclib_id_tracks_conflict": "--lrclib-id 不能与 --tracks 或手动 --artist/--title 模式同时使用",
        "validate.tracks_manual_conflict": "--tracks 不能与手动 --artist/--title 模式同时使用",
        "validate.manual_requires_artist_title": "手动模式需要同时提供 --artist 和 --title",
        "validate.down_missing_input": "需要提供 --lrclib-id、--tracks，或同时提供 --artist/--title",
        "validate.skip_overwrite_conflict": "--skip-existing 和 --overwrite 不能同时使用",
        "validate.lrclib_id_search_conflict": "--lrclib-id 不能与 --query/--title/--artist/--album 同时使用",
        "validate.search_missing_input": "需要提供 --lrclib-id 或 --query/--title 之一",

        # ── cli/main.py ──
        "cli.description": "围绕 LRCLIB 的上传、下载、搜索、检查和清洗歌词的命令行工具。",
        "cli.epilog": (
            "示例：\n"
            "  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n"
            '  pylrclib down --artist "Aimer" --title "Ref:rain" --save-mode both\n'
            '  pylrclib search --query "歌手 歌名"\n'
            "  pylrclib cleanse ./lyrics --write"
        ),
        "cli.lang.help": "命令输出和提示的界面语言。",
        "cli.subcommands.title": "子命令",
        "cli.subcommands.description": "选择以下命令之一。",
        "cli.interrupted": "用户中断",

        # ── cli/helptext.py ──
        "cli.default_template": "默认：{default}。",
        "cli.help.preview_lines": "预览纯文本或滚动歌词时显示的歌词行数。",
        "cli.help.max_retries": "对可重试的 LRCLIB 请求的最大 HTTP 重试次数。",
        "cli.help.user_agent": "发送到 LRCLIB 的 HTTP User-Agent 头。",
        "cli.help.api_base": "LRCLIB API 的基础 URL。",
        "cli.help.yes": "对确认提示自动回答是，否则会在写入或发布前询问。",
        "cli.help.non_interactive": "禁用交互式提示，使用安全的自动决策。",

        # ── commands/up.py ──
        "cmd.up.help": "上传本地歌词到 LRCLIB",
        "cmd.up.description": "运行完整的上传工作流。该命令会扫描音频或 YAML 元数据，解析本地纯文本和滚动歌词，检查 LRCLIB 上的现有记录，并可选地发布新歌词。",
        "cmd.up.epilog": (
            "示例：\n"
            "  pylrclib up --tracks ./music --lyrics-dir ./lyrics --yes\n"
            "  pylrclib up --tracks ./tracks --plain-dir ./plain --synced-dir ./lrc --lyrics-mode mixed\n"
            "  pylrclib up -d ./tracks ./lyrics"
        ),
        "cmd.up.arg.tracks": "包含要上传的音频文件或 YAML 元数据文件的目录。",
        "cmd.up.arg.lyrics_dir": "可能同时包含纯文本歌词和 .lrc 滚动歌词的共享歌词目录。",
        "cmd.up.arg.plain_dir": "搜索纯文本歌词（如 .txt 文件）的目录。",
        "cmd.up.arg.synced_dir": "搜索滚动歌词（如 .lrc 文件）的目录。",
        "cmd.up.arg.done_tracks": "上传成功后，处理完成的音轨文件移动到的目录。",
        "cmd.up.arg.done_lrc": "上传后处理完成的歌词文件移动到的目录。",
        "cmd.up.arg.follow": "将匹配的歌词文件跟随音轨目标移动，而不是使用 --done-lrc。",
        "cmd.up.arg.rename": "移动时将匹配的歌词文件重命名为与音轨文件相同的基础名称。",
        "cmd.up.arg.cleanse": "上传前清洗 .lrc 滚动歌词内容，使无效或杂乱的歌词行规范化。",
        "cmd.up.arg.cleanse_write": "将清洗后的滚动歌词写回磁盘。需要同时使用 --cleanse。",
        "cmd.up.arg.allow_non_lrc": "允许手动选择的非 .lrc 扩展名的滚动歌词文件。",
        "cmd.up.arg.ignore_duration_mismatch": "当 LRCLIB 返回的记录的时长与本地音轨不一致时，不警告也不停止。",
        "cmd.up.arg.lyrics_mode": "上传策略：auto 选择最佳可用歌词，plain 只上传纯文本，synced 只上传 LRC，mixed 需要同时有二者，instrumental 发布纯音乐标记。",
        "cmd.up.arg.allow_derived_plain": "当没有单独的纯文本文件时，允许从 LRC 滚动歌词中派生纯文本歌词。",
        "cmd.up.arg.no_derived_plain": "禁止从滚动歌词中派生纯文本歌词。",
        "cmd.up.arg.default": "快捷模式：相当于设置音轨目录和一个共享歌词目录，并同时启用 follow、rename 和 cleanse。",
        "cmd.up.arg.match": "匹配模式：启用 follow、rename 和 cleanse，同时仍使用各自解析的目录。",

        # ── commands/down.py ──
        "cmd.down.help": "从 LRCLIB 下载歌词",
        "cmd.down.description": "通过扫描本地音轨、手动输入歌手/歌名或指定 LRCLIB 记录 ID 来从 LRCLIB 下载歌词。",
        "cmd.down.epilog": (
            "示例：\n"
            "  pylrclib down --tracks ./music --output-dir ./lyrics\n"
            '  pylrclib down --artist "Aimer" --title "Ref:rain" --save-mode both\n'
            "  pylrclib down --lrclib-id 12345 --output-dir ./lyrics"
        ),
        "cmd.down.arg.tracks": "包含音频或 YAML 文件的目录，其元数据将用于 LRCLIB 查询。",
        "cmd.down.arg.artist": "用于单曲下载的手动指定的歌手名称。",
        "cmd.down.arg.title": "用于单曲下载的手动指定的歌曲名称。",
        "cmd.down.arg.album": "可选，用于改善手动下载匹配精度的专辑名称。",
        "cmd.down.arg.duration": "可选，用于改善手动下载匹配精度的音轨时长（秒）。",
        "cmd.down.arg.lrclib_id": "按数字 ID 精确获取某条 LRCLIB 记录，而不是按元数据搜索。",
        "cmd.down.arg.output_dir": "下载的歌词文件的基础输出目录。",
        "cmd.down.arg.plain_dir": "写入纯文本歌词的目录。未指定时，纯文本歌词写入 --output-dir。",
        "cmd.down.arg.synced_dir": "写入 .lrc 滚动歌词的目录。未指定时，滚动歌词写入 --output-dir。",
        "cmd.down.arg.save_mode": "如何保存获取的歌词：auto 选择最佳可用输出，plain 只写纯文本，synced 只写 .lrc，both 在可用时都写。",
        "cmd.down.arg.naming": "输出命名策略：auto 尽可能使用本地音轨基础名称，track-basename 强制使用本地基础名称，artist-title 使用「歌手 - 歌名」格式。",
        "cmd.down.arg.skip_existing": "不覆盖输出目录中已存在的文件。",
        "cmd.down.arg.overwrite": "覆盖输出目录中已存在的文件。",
        "cmd.down.arg.allow_derived_plain": "当 LRCLIB 只返回滚动歌词时，允许从其中生成纯文本歌词。",
        "cmd.down.arg.no_derived_plain": "禁止从滚动歌词生成纯文本歌词。",

        # ── commands/search.py ──
        "cmd.search.help": "搜索 LRCLIB 并预览远程歌词记录",
        "cmd.search.description": "通过自由文本查询或元数据字段搜索 LRCLIB，或通过 LRCLIB ID 获取精确记录。",
        "cmd.search.epilog": (
            "示例：\n"
            '  pylrclib search --query "歌手 歌名"\n'
            '  pylrclib search --artist "Aimer" --title "Ref:rain" --album daydream\n'
            "  pylrclib search --lrclib-id 12345 --json"
        ),
        "cmd.search.arg.query": "发送到 LRCLIB 搜索的自由文本查询。",
        "cmd.search.arg.title": "用于结构化 LRCLIB 搜索的歌曲名称。",
        "cmd.search.arg.artist": "用于结构化 LRCLIB 搜索的歌手名称。",
        "cmd.search.arg.album": "用于结构化 LRCLIB 搜索的专辑名称。",
        "cmd.search.arg.lrclib_id": "按数字 ID 获取精确的 LRCLIB 记录。",
        "cmd.search.arg.limit": "显示的 LRCLIB 搜索结果的最大数量。",
        "cmd.search.arg.json": "输出原始 JSON 格式的搜索结果，而不是格式化预览视图。",

        # ── commands/inspect.py ──
        "cmd.inspect.help": "检查输入和本地歌词匹配情况（不上传）",
        "cmd.inspect.description": "检查本地音频或 YAML 输入，显示匹配的歌词候选项，并预览解析后的歌词包，不会上传任何内容。",
        "cmd.inspect.epilog": (
            "示例：\n"
            "  pylrclib inspect --tracks ./music --lyrics-dir ./lyrics\n"
            "  pylrclib inspect --tracks ./music --plain-dir ./plain --synced-dir ./lrc --show-all-candidates"
        ),
        "cmd.inspect.arg.tracks": "包含要检查的音频或 YAML 输入的目录。",
        "cmd.inspect.arg.lyrics_dir": "可能同时包含纯文本歌词和滚动歌词的共享歌词目录。",
        "cmd.inspect.arg.plain_dir": "搜索纯文本歌词候选项的目录。",
        "cmd.inspect.arg.synced_dir": "搜索滚动歌词候选项的目录。",
        "cmd.inspect.arg.lyrics_mode": "用于决定选择哪个匹配歌词包的解析策略。",
        "cmd.inspect.arg.preview_lines": "每个解析后的歌词包预览的行数。",
        "cmd.inspect.arg.show_all_candidates": "打印所有匹配的纯文本和滚动歌词候选项，而不是只打印最佳匹配。",
        "cmd.inspect.found_items": "找到 {count} 个项目。",

        # ── commands/cleanse.py ──
        "cmd.cleanse.help": "清洗 LRC 文件（不上传）",
        "cmd.cleanse.description": "通过删除无效、重复或杂乱的歌词行来清洗本地 .lrc 文件。此命令不会上传任何内容。",
        "cmd.cleanse.epilog": (
            "示例：\n"
            "  pylrclib cleanse ./lyrics\n"
            "  pylrclib cleanse ./lyrics --write\n"
            "  pylrclib cleanse song.lrc another.lrc"
        ),
        "cmd.cleanse.arg.paths": "一个或多个需要递归清洗的 .lrc 文件或目录。",
        "cmd.cleanse.arg.lrc_dir": "需要递归清洗的 .lrc 文件目录。",
        "cmd.cleanse.arg.write": "将清洗后的输出写回原文件。不使用此标志时，命令仅预览清洗结果。",
        "cmd.cleanse.arg.preview_lines": "每个处理文件预览清洗后歌词的行数。",
        "cmd.cleanse.no_lrc_found": "未找到 LRC 文件",
        "cmd.cleanse.summary": "摘要：{summary}",

        # ── commands/doctor.py ──
        "cmd.doctor.help": "诊断当前工作区和已解析的配置",
        "cmd.doctor.description": "与上传工作流完全一致地解析配置，然后检查目录和输入中的常见问题。",
        "cmd.doctor.epilog": (
            "示例：\n"
            "  pylrclib doctor --tracks ./music --lyrics-dir ./lyrics\n"
            "  pylrclib doctor -d ./tracks ./lyrics\n"
            "  pylrclib doctor --tracks ./music --plain-dir ./plain --synced-dir ./lrc"
        ),
        "cmd.doctor.arg.tracks": "包含要验证的音频或 YAML 输入的目录。",
        "cmd.doctor.arg.lyrics_dir": "可能同时包含纯文本歌词和滚动歌词文件的共享歌词目录。",
        "cmd.doctor.arg.plain_dir": "要验证纯文本歌词的目录。",
        "cmd.doctor.arg.synced_dir": "要验证 .lrc 滚动歌词的目录。",
        "cmd.doctor.arg.done_tracks": "上传后处理完成的音轨文件将移动到的目录。",
        "cmd.doctor.arg.done_lrc": "上传后处理完成的歌词文件将移动到的目录。",
        "cmd.doctor.arg.follow": "验证歌词文件跟随音轨目标移动的上传模式。",
        "cmd.doctor.arg.rename": "验证歌词文件重命名为音轨基础名称的上传模式。",
        "cmd.doctor.arg.cleanse": "验证上传前清洗滚动歌词的上传模式。",
        "cmd.doctor.arg.lyrics_mode": "要针对当前工作区验证的上传策略。",
        "cmd.doctor.arg.default": "快捷模式，验证使用一个共享歌词目录的默认上传预设。",
        "cmd.doctor.arg.match": "验证同时启用 follow、rename 和 cleanse 的匹配预设。",
        "cmd.doctor.arg.preview_lines": "上传类命令将显示的歌词预览行数。",
        "cmd.doctor.arg.max_retries": "上传工作流将使用的最大 HTTP 重试次数。",
        "cmd.doctor.arg.user_agent": "上传工作流将发送的 HTTP User-Agent 头。",
        "cmd.doctor.arg.api_base": "上传工作流将调用的 LRCLIB API 基础 URL。",
        "cmd.doctor.resolved_config": "已解析的配置：",
        "cmd.doctor.found_counts": "找到 音频={audio}, yaml={yaml}, 纯文本={plain}, 滚动={synced}, 有效输入={items}",
        "cmd.doctor.finished_ok": "doctor 诊断完成，未发现致命问题",
        "cmd.doctor.tracks_not_exist": "tracks_dir 目录不存在：{path}",
        "cmd.doctor.follow_done_conflict": "follow_track 和 done_lrc_dir 不应同时使用",

        # ── interaction.py ──
        "prompt.yes_no_yes_default": "[Y/n]",
        "prompt.yes_no_no_default": "[y/N]",
        "prompt.choose_range": "选择 1-{max}（按 Enter 跳过）：",
        "prompt.invalid_input": "无效输入，请重试。",
        "prompt.missing_lyrics_action": "未找到本地歌词。请选择 [s]跳过 / [p]纯文本文件 / [y]滚动文件 / [i]纯音乐 / [q]退出：",
        "prompt.enter_path": "输入 {expected} 文件路径：",
        "prompt.invalid_file": "无效文件：{path}",

        # ── workflows/up.py ──
        "wf.up.preview_label": "--- {label} ---",
        "wf.up.empty": "[空]",
        "wf.up.lines_truncated": "...（共 {count} 行）",
        "wf.up.processing": "正在处理 {label}",
        "wf.up.cached_kind": "缓存",
        "wf.up.external_kind": "外部",
        "wf.up.local_kind": "本地",
        "wf.up.accepted_cache": "已接受缓存记录；跳过上传",
        "wf.up.uploaded_external": "已上传外部歌词",
        "wf.up.external_failed": "外部上传失败；继续本地流程",
        "wf.up.plain_candidates": "纯文本候选项：",
        "wf.up.synced_candidates": "滚动歌词候选项：",
        "wf.up.use_directly": "直接使用 {kind} 歌词？",
        "wf.up.duration_differs": "{kind} 歌词时长相差 {diff} 秒。是否仍然使用？",
        "wf.up.skipping": "跳过上传 {label}：{reason}",
        "wf.up.confirm_instrumental": "作为纯音乐上传？",
        "wf.up.confirm_upload": "使用 {mode} 策略上传本地歌词？",
        "wf.up.upload_completed": "上传完成",
        "wf.up.upload_failed": "上传失败",
        "wf.up.moved_audio": "已将音频移动到 {path}",
        "wf.up.moved_lyrics": "已将歌词文件移动到 {path}",
        "wf.up.remote_skipped": "已跳过远程歌词：{reason}",
        "wf.up.no_inputs": "未找到支持的音频或 YAML 文件",

        # ── lyrics types for prompts ──
        "lyrics.plain_type": "纯文本歌词",
        "lyrics.synced_type": "滚动歌词",

        # ── workflows/down.py ──
        "wf.down.downloading": "正在下载 {label}",
        "wf.down.no_lyrics": "未找到 {label} 的歌词",
        "wf.down.wrote": "已写入 {path}",
        "wf.down.finished": "下载完成：已写入 {count} 个文件",
        "wf.down.instrumental": "LRCLIB 报告为纯音乐曲目：{artist} - {track}",
        "wf.down.duration_differs": "{track} 的时长相差 {diff} 秒。是否仍然保存？",
        "wf.down.remote_plain": "远程 plainLyrics",
        "wf.down.remote_synced": "远程 syncedLyrics",
        "wf.down.no_inputs": "未找到支持的音频或 YAML 文件",

        # ── workflows/search.py ──
        "wf.search.no_results": "没有搜索结果",

        # ── logging_utils.py ──
        "log.info": "信息",
        "log.warn": "警告",
        "log.error": "错误",
        "log.debug": "调试",

        # ── models/lyrics.py ──
        "model.id_prefix": "#{id} ",
        "model.separator": " - ",
        "model.album_suffix": " [{album}]",
        "model.duration_suffix": " ({duration}秒)",
        "model.unknown": "<未知>",

        # ── lrc/parser.py ──
        "lrc.no_valid_timestamps": "无有效时间戳",
        "lrc.read_failed": "读取失败",
        "lrc.empty_after_cleanse": "清洗后为空",
        "lrc.status.invalid": "无效",
        "lrc.status.unchanged": "未更改",
        "lrc.status.updated": "已更新",
        "lrc.status.failed": "失败",
        "lrc.read_error": "无法读取 LRC {path}：{exc}",

        # ── lyrics/loader.py ──
        "lyrics.empty_text": "空文本",
        "lyrics.instrumental_detected": "检测到纯音乐标记",
        "lyrics.invalid_plain": "无效的纯文本候选项",
        "lyrics.invalid_synced": "无效的滚动歌词候选项",
        "lyrics.incomplete_mixed": "混合歌词不完整",
        "lyrics.no_plain": "无纯文本歌词",
        "lyrics.no_synced": "无滚动歌词",
        "lyrics.empty_record": "空记录",

        # ── interaction.py choose labels ──
        "prompt.multiple_plain": "找到多个纯文本歌词候选项：",
        "prompt.multiple_synced": "找到多个滚动歌词候选项：",

        # ── cleaner.py / mover.py ──
        "fs.move_failed": "移动失败 {src} -> {dst_dir}：{exc}",
        "fs.delete_dir_failed": "删除空目录失败 {dir}：{exc}",

        # ── api/retry messages ──
        "api.request_error": "{label} 请求错误，第 {attempt}/{retries} 次尝试：{exc}；{delay:.1f} 秒后重试",
        "api.request_failed": "{label} 在 {attempts} 次尝试后失败：{exc}",
        "api.invalid_json": "{label} 返回了无效的 JSON：{text}",
        "api.http_fail_final": "{label} 失败，HTTP {status} {text}",
        "api.http_fail_retry": "{label} 失败，HTTP {status}；{delay:.1f} 秒后重试",

        # ── api/publish.py ──
        "api.publish_challenge": "请求发布挑战",
        "api.upload_lyrics": "上传歌词",
        "api.upload_instrumental": "上传纯音乐标记",
        "api.publish_failed": "{label} 在 {attempts} 次尝试后失败：{exc}",
        "api.publish_http_fail": "{label} 失败，HTTP {status}：{text}",
    },
}


def get(key: str, locale: str = "en_US", **kwargs: object) -> str:
    """Look up a translated string for *locale*, falling back to en_US then to *key* itself."""
    table = STRINGS.get(locale, STRINGS["en_US"])
    text = table.get(key)
    if text is None:
        text = STRINGS["en_US"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
