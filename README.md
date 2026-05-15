# pylrclib

A multi-command CLI around LRCLIB for searching, downloading, inspecting, cleansing, and publishing lyrics.

`pylrclib` treats lyrics as four explicit states:

- `plain`: unsynced plain-text lyrics
- `synced`: timed LRC lyrics
- `mixed`: both plain and synced lyrics are available
- `instrumental`: instrumental / no-vocals track

That shared model drives all major commands:

- `pylrclib search`: search LRCLIB and preview remote results
- `pylrclib down`: download lyrics from LRCLIB to local files
- `pylrclib up`: publish local lyrics to LRCLIB
- `pylrclib inspect`: inspect local matching and classification without publishing
- `pylrclib cleanse`: normalize `.lrc` files
- `pylrclib doctor`: diagnose workspace and configuration issues

---

## Installation

### From PyPI (Recommended)

```bash
pip install pylrclib-cli
```

### From source

```bash
pip install -e .
```

### Entry points

```bash
pylrclib --help
python -m pylrclib --help
```

### Language / i18n

`pylrclib` supports English (`en_US`) and Chinese (`zh_CN`). The interface language is auto-detected from your system `$LANG` environment variable.

```bash
# Use Chinese
pylrclib --lang zh_CN --help

# Use English
pylrclib --lang en_US --help

# Auto-detect (default)
pylrclib --lang auto --help

# Or set once per session
export PYLRCLIB_LANG=zh_CN
pylrclib --help
```

---

## Command overview

```bash
pylrclib search ...
pylrclib down ...
pylrclib up ...
pylrclib inspect ...
pylrclib cleanse ...
pylrclib doctor ...
```

---

## `search`: search LRCLIB and preview remote records

Use `search` when you want to inspect LRCLIB results before downloading or publishing.

### Query search

```bash
pylrclib search --query "song title"
pylrclib search --title "Song Title" --artist "Artist Name"
```

### Lookup by LRCLIB id

```bash
pylrclib search --lrclib-id 12345
```

### Useful parameters

```bash
--query TEXT
--title TEXT
--artist TEXT
--album TEXT
--lrclib-id N
--limit N
--preview-lines N
--json
--api-base URL
```

---

## `down`: download lyrics from LRCLIB

`down` supports three input modes:

1. Scan local audio / YAML metadata and query LRCLIB
2. Manually specify artist/title metadata
3. Fetch one exact record with `--lrclib-id`

### Download based on local music metadata

```bash
pylrclib down \
  --tracks ./music \
  --output-dir ./lyrics_downloaded
```

### Download one song manually

```bash
pylrclib down \
  --artist "Artist Name" \
  --title "Song Title" \
  --album "Album Name" \
  --duration 180 \
  --output-dir ./lyrics_downloaded
```

### Download one exact LRCLIB record

```bash
pylrclib down \
  --lrclib-id 12345 \
  --output-dir ./lyrics_downloaded \
  --save-mode both
```

### Save strategy

```bash
--save-mode auto|plain|synced|both
```

Default behavior:

- `auto`
  - if LRCLIB provides synced lyrics, save `.lrc`
  - if only plain lyrics exist, save `.txt`
  - if instrumental, report it and do not write lyric files
- `plain`: save only `.txt`
- `synced`: save only `.lrc`
- `both`: save both `.txt` and `.lrc` when available

### Naming strategy

```bash
--naming auto|track-basename|artist-title
```

When scanning local files, `auto` prefers the track basename. In manual or id-based downloads, `auto` falls back to `Artist - Title`.

---

## `up`: publish local lyrics to LRCLIB

`up` runs the full upload workflow:

1. Discover audio files or YAML metadata
2. Check LRCLIB cached and external matches
3. Resolve local plain and synced lyric candidates
4. Classify lyrics as `plain`, `synced`, `mixed`, `instrumental`, or `invalid`
5. Build an upload plan from `--lyrics-mode`
6. Publish lyrics or mark the track instrumental
7. Optionally move or rename processed files

### Basic usage

```bash
pylrclib up --tracks ./music --lyrics-dir ./lyrics
```

### Recommended split-directory usage

```bash
pylrclib up \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc \
  --done-lrc ./done_lyrics \
  --lyrics-mode auto \
  --cleanse
```

### Upload strategy

```bash
--lyrics-mode auto|plain|synced|mixed|instrumental
```

Behavior summary:

- `auto`
  - plain + synced => publish both
  - only synced => publish synced and optionally derive plain text
  - only plain => publish plain only
  - explicit instrumental markers => publish as instrumental
  - invalid lyrics => skip
- `plain`: publish plain lyrics only
- `synced`: publish synced lyrics and optionally derived plain text
- `mixed`: require both plain and synced lyrics
- `instrumental`: force instrumental upload

### Local lyric matching

`up` searches for two lyric types separately:

- plain candidates:
  - `.txt`
  - `.lyrics`
  - `.lyric`
- synced candidates:
  - `.lrc`

Matching sources include:

1. same basename as the audio / YAML file
2. YAML-declared filenames
3. normalized `Artist - Title.*` matches
4. interactive selection when multiple candidates exist

### Important parameters

```bash
--tracks PATH
--lyrics-dir PATH
--plain-dir PATH
--synced-dir PATH
--done-tracks PATH
--done-lrc PATH
-f, --follow
-r, --rename
-c, --cleanse
--cleanse-write
--lyrics-mode auto|plain|synced|mixed|instrumental
--allow-derived-plain / --no-derived-plain
--ignore-duration-mismatch
--yes
--non-interactive
```

### YAML input format

```yaml
track: Song Title
artist: Artist Name
album: Album Name
duration: 180
plain_file: song.txt
synced_file: song.lrc
lyrics_file: song.lrc
lrc_file: song.lrc
```

---

## `inspect`: inspect local matching and classification

`inspect` shows what the tool would use locally, without publishing.

```bash
pylrclib inspect \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc \
  --show-all-candidates
```

This is useful for debugging why a track resolved to `plain`, `mixed`, or `invalid`.

---

## `cleanse`: normalize `.lrc` files

`cleanse` cleans synced lyrics safely.

```bash
pylrclib cleanse ./lyrics_lrc
pylrclib cleanse ./lyrics_lrc --write
```

Recommended behavior:

- use `cleanse` to preview / analyze normalization
- use `--write` only when you really want to rewrite files in place

Invalid files are not blindly rewritten into empty files.

---

## `doctor`: diagnose the current workspace

```bash
pylrclib doctor \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc
```

`doctor` prints resolved configuration, counts discovered inputs, and highlights obvious workflow conflicts.

---

## Environment variables

Supported environment variables include:

```text
PYLRCLIB_TRACKS_DIR
PYLRCLIB_LYRICS_DIR
PYLRCLIB_PLAIN_DIR
PYLRCLIB_SYNCED_DIR
PYLRCLIB_DONE_TRACKS_DIR
PYLRCLIB_DONE_LRC_DIR
PYLRCLIB_OUTPUT_DIR
PYLRCLIB_ARTIST
PYLRCLIB_TITLE
PYLRCLIB_ALBUM
PYLRCLIB_DURATION
PYLRCLIB_LRCLIB_ID
PYLRCLIB_API_BASE
PYLRCLIB_USER_AGENT
PYLRCLIB_PREVIEW_LINES
PYLRCLIB_MAX_HTTP_RETRIES
```

---

## Development

Run tests:

```bash
pytest -q
```

Install dev dependencies:

```bash
pip install -e .[dev]
```

---

## 中文说明

`pylrclib` 是一个围绕 LRCLIB 的多子命令命令行工具，可用于搜索、下载、检查、清洗和上传歌词。

它把歌词明确建模成四种状态：

- `plain`：纯文本歌词，无时间轴
- `synced`：滚动歌词，带时间轴（LRC）
- `mixed`：同时拥有纯文本歌词和滚动歌词
- `instrumental`：纯音乐 / 无人声

对应的主要命令是：

- `pylrclib search`：搜索 LRCLIB 并预览远端结果
- `pylrclib down`：从 LRCLIB 下载歌词到本地
- `pylrclib up`：把本地歌词上传到 LRCLIB
- `pylrclib inspect`：只检查本地匹配与分类结果
- `pylrclib cleanse`：清洗和标准化 `.lrc`
- `pylrclib doctor`：诊断工作区和配置问题

### `search`

```bash
pylrclib search --query "歌名"
pylrclib search --title "歌名" --artist "歌手"
pylrclib search --lrclib-id 12345
```

适合用来先确认 LRCLIB 上到底有哪些候选结果，再决定是否下载或上传。

### `down`

`down` 现在支持三种输入方式：

1. 读取本地音频 / YAML 元数据后去 LRCLIB 查询
2. 手动指定 `--artist` / `--title`
3. 通过 `--lrclib-id` 精确抓取某一条 LRCLIB 记录

示例：

```bash
pylrclib down --tracks ./music --output-dir ./lyrics_downloaded
pylrclib down --artist "歌手" --title "歌名" --output-dir ./lyrics_downloaded
pylrclib down --lrclib-id 12345 --output-dir ./lyrics_downloaded --save-mode both
```

保存策略：

```bash
--save-mode auto|plain|synced|both
```

- `auto`：有滚动歌词就保存 `.lrc`；只有纯文本就保存 `.txt`
- `plain`：只保存 `.txt`
- `synced`：只保存 `.lrc`
- `both`：两种都保存

### `up`

`up` 会按以下步骤工作：

1. 扫描音频文件或 YAML 元数据
2. 查询 LRCLIB 缓存与外部歌词候选
3. 分别查找本地 plain / synced 歌词
4. 自动识别歌词类型
5. 根据 `--lyrics-mode` 决定上传策略
6. 上传成功后按配置移动或重命名文件

推荐用法：

```bash
pylrclib up \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc \
  --done-lrc ./done_lyrics \
  --lyrics-mode auto \
  --cleanse
```

上传策略：

```bash
--lyrics-mode auto|plain|synced|mixed|instrumental
```

默认 `auto` 的逻辑是：

- 同时有 plain 和 synced：一起上传
- 只有 synced：上传滚动歌词，并可从中派生纯文本歌词
- 只有 plain：只上传纯文本歌词
- 明确识别为纯音乐：按纯音乐上传
- 无效歌词：跳过，不再自动当成纯音乐

### `inspect` / `cleanse` / `doctor`

- `inspect`：查看本地匹配到了哪些歌词文件、最终被识别为什么类型
- `cleanse`：清洗 `.lrc`，并避免把无效文件误清空
- `doctor`：查看解析后的配置和当前目录中的可用输入数量

---

## License

MIT
