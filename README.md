# pylrclib

`pylrclib` 是一个围绕 [LRCLIB](https://lrclib.net/) 的多子命令命令行工具，用来：

- 从本地歌词上传到 LRCLIB
- 从 LRCLIB 下载歌词到本地
- 检查本地音频 / YAML 元数据 / 歌词匹配结果
- 清洗和标准化 `.lrc` 文件
- 诊断工作区和配置

它把“歌词”明确建模成四种状态：

- `plain`：纯文本歌词，无时间轴
- `synced`：滚动歌词，带时间轴（LRC）
- `mixed`：同时拥有 `plain` 和 `synced`
- `instrumental`：纯音乐

这套模型同时服务于：

- `pylrclib up`：上传时自动决定传 plain、synced、mixed 还是 instrumental
- `pylrclib down`：下载时按策略落盘成 `.txt`、`.lrc` 或两者都保存

---

## 1. 安装

### 从源码安装

```bash
pip install -e .
```

### 运行入口

```bash
pylrclib --help
python -m pylrclib --help
```

---

## 2. 命令总览

```bash
pylrclib up ...
pylrclib down ...
pylrclib cleanse ...
pylrclib inspect ...
pylrclib doctor ...
```

---

## 3. `up`：上传本地歌词到 LRCLIB

`up` 会：

1. 扫描音频文件或 YAML 元数据
2. 查询 LRCLIB 缓存与外部候选歌词
3. 在本地目录中寻找 `plain` / `synced` 歌词
4. 自动判断每首歌的歌词类型
5. 根据 `--lyrics-mode` 决定最终上传策略
6. 上传成功后移动/重命名歌词文件

### 3.1 最简单用法

```bash
pylrclib up --tracks ./music --lyrics-dir ./lyrics
```

如果 `--lyrics-dir` 同时包含 `.txt` 和 `.lrc`，`up` 会自动尝试为同一首歌合并两者。

### 3.2 推荐用法：plain / synced 分目录

```bash
pylrclib up \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc \
  --done-lrc ./done_lyrics \
  --lyrics-mode auto \
  --cleanse
```

### 3.3 上传策略：`--lyrics-mode`

```bash
--lyrics-mode auto|plain|synced|mixed|instrumental
```

默认是：

```bash
--lyrics-mode auto
```

各模式含义：

- `auto`
  - 有 plain + synced → 同时上传两者
  - 只有 synced → 上传 synced，并默认派生 plain
  - 只有 plain → 只上传 plain
  - 明确识别为纯音乐 → 上传 instrumental
  - 无效歌词 → 跳过

- `plain`
  - 只上传 plain
  - 没有 plain 时跳过

- `synced`
  - 上传 synced
  - 默认可同时带上由 synced 派生出的 plain

- `mixed`
  - 必须同时拥有 plain 和 synced
  - 任一缺失则跳过

- `instrumental`
  - 强制按纯音乐上传

### 3.4 本地歌词查找规则

`up` 会分别寻找 plain 和 synced 候选：

- `plain`
  - `.txt`
  - `.lyrics`
  - `.lyric`

- `synced`
  - `.lrc`

匹配顺序大致为：

1. 与音频 / YAML 同 basename 的文件
2. YAML 中显式指定的文件
3. `Artist - Title.*` 模式匹配
4. 多候选时交互选择；非交互时优先第一个匹配

### 3.5 纯文本与滚动歌词的识别逻辑

#### 识别为 `synced`
- 至少存在合法时间戳
- 能成功解析为 LRC

#### 识别为 `plain`
- 没有合法时间戳
- 但存在非空正文文本

#### 识别为 `instrumental`
- 明确命中纯音乐语义，例如：
  - `纯音乐，请欣赏`
  - `instrumental`

#### 识别为 `invalid`
- 空文件
- 只有无效文本
- 无法作为 plain 或 synced 使用

> `invalid` 不会再被自动当成 `instrumental`。

### 3.6 常用参数

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
--preview-lines N
--api-base URL
--max-retries N
```

### 3.7 YAML 输入

支持的 YAML 字段：

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

说明：

- `plain_file`：显式指定纯文本歌词
- `synced_file`：显式指定滚动歌词
- `lyrics_file` / `lrc_file`：兼容地指向一个歌词文件，通常是 `.lrc`

---

## 4. `down`：从 LRCLIB 下载歌词

`down` 会：

1. 从本地音频 / YAML 读取歌曲元数据，或手动指定 artist/title
2. 调 LRCLIB 查询歌词
3. 把返回结果映射为 `plain` / `synced` / `mixed` / `instrumental`
4. 按 `--save-mode` 决定是否保存 `.txt`、`.lrc` 或两者都保存

### 4.1 从本地音乐库下载

```bash
pylrclib down \
  --tracks ./music \
  --output-dir ./lyrics_downloaded
```

### 4.2 手动下载单曲

```bash
pylrclib down \
  --artist "Artist Name" \
  --title "Song Title" \
  --album "Album Name" \
  --duration 180 \
  --output-dir ./lyrics_downloaded
```

### 4.3 下载保存策略：`--save-mode`

```bash
--save-mode auto|plain|synced|both
```

默认：

```bash
--save-mode auto
```

语义：

- `auto`
  - LRCLIB 有 synced → 保存 `.lrc`
  - 只有 plain → 保存 `.txt`
  - instrumental → 默认不落盘

- `plain`
  - 只保存 `.txt`

- `synced`
  - 只保存 `.lrc`

- `both`
  - 同时保存 `.txt` 与 `.lrc`
  - 如 LRCLIB 只有 synced，且允许派生 plain，则会自动生成 `.txt`

### 4.4 命名策略：`--naming`

```bash
--naming auto|track-basename|artist-title
```

默认：

- 基于本地音频/YAML：`track-basename`
- 手动模式：`artist-title`

例子：

```text
song.mp3      -> song.lrc / song.txt
Artist - Song -> Artist - Song.lrc / Artist - Song.txt
```

### 4.5 覆盖策略

```bash
--skip-existing
--overwrite
```

两者不能同时使用。

---

## 5. `cleanse`：批量清洗 `.lrc`

`cleanse` 只处理 `.lrc` 文件，不上传。

```bash
# 只预览，不写回
pylrclib cleanse ./lyrics

# 清洗并覆盖
pylrclib cleanse ./lyrics --write
```

清洗规则：

- 统一换行与编码读取
- 删除 credit 行（作词、作曲等）
- 删除同时间戳翻译行
- 保留标准化后的 synced 内容

安全策略：

- 无合法时间戳的文件会标记为 `invalid`
- `invalid` 文件不会被覆盖
- 清洗结果为空但原文件非空时，不会盲目写回

---

## 6. `inspect`：检查本地歌词解析结果

```bash
pylrclib inspect \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc
```

它会输出：

- 发现的输入项
- plain / synced 候选文件
- 最终识别的歌词类型
- plain / synced 预览
- warnings

这个命令不会上传，也不会移动文件。

---

## 7. `doctor`：诊断工作区与配置

```bash
pylrclib doctor \
  --tracks ./music \
  --plain-dir ./lyrics_plain \
  --synced-dir ./lyrics_lrc
```

会显示：

- 解析后的配置
- 各目录是否存在
- 音频 / YAML / plain / synced 文件数量
- 有效输入数量
- 常见冲突提示

---

## 8. 环境变量

支持以下环境变量：

```bash
export PYLRCLIB_TRACKS_DIR=/data/music
export PYLRCLIB_LYRICS_DIR=/data/lyrics
export PYLRCLIB_PLAIN_DIR=/data/lyrics_plain
export PYLRCLIB_SYNCED_DIR=/data/lyrics_lrc
export PYLRCLIB_DONE_TRACKS_DIR=/data/done_music
export PYLRCLIB_DONE_LRC_DIR=/data/done_lyrics
export PYLRCLIB_OUTPUT_DIR=/data/downloaded_lyrics
export PYLRCLIB_PREVIEW_LINES=15
export PYLRCLIB_MAX_HTTP_RETRIES=8
export PYLRCLIB_USER_AGENT='MyUploader/1.0'
export PYLRCLIB_API_BASE=https://lrclib.net/api
```

统一优先级：

```text
CLI 参数 > 环境变量 > 默认值
```

---

## 9. 项目结构

```text
pylrclib/
  cli/          CLI 入口
  commands/     子命令
  workflows/    上传/下载业务编排
  api/          LRCLIB 查询、重试、PoW、发布
  lrc/          LRC 解析、清洗、匹配
  lyrics/       歌词 bundle 加载与写入
  fs/           文件移动与清理
  models/       元数据与歌词模型
tests/          单元测试 + smoke test
```

---

## 10. 开发与测试

### 运行测试

```bash
pytest
```

### 当前 smoke test 覆盖

- `up`：YAML + plain/synced 混合上传
- `up`：plain-only 自动上传
- `down`：从 LRCLIB 抓取并同时落 `.txt` + `.lrc`
- `cleanse`
- `inspect`
- `doctor`

---

## 11. 设计原则

### 11.1 `up` 不再把无效歌词误当纯音乐

`invalid`、`plain`、`synced`、`instrumental` 明确区分。

### 11.2 `down` 和 `up` 共用同一套歌词模型

所以两边对 plain / synced 的理解一致。

### 11.3 纯文本歌词与滚动歌词可并存

同一首歌可以同时拥有：

- `song.txt`
- `song.lrc`

`pylrclib` 会尽量把它们视为一个逻辑整体，而不是互相覆盖。
