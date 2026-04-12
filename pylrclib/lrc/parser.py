from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..logging_utils import log_error

TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}\.\d{2,3}\]")
EXTENDED_TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}(?:\.\d{1,3}(?:-\d{1,3})?)?\]")
HEADER_TAG_RE = re.compile(r"^\[[a-zA-Z]{2,3}:.+\]$")
CREDIT_KEYWORDS = (
    "作词", "作曲", "编曲", "混音", "缩混", "录音", "母带", "制作", "监制", "和声",
    "配唱", "制作人", "演唱", "伴奏", "编配", "吉他", "贝斯", "鼓", "键盘", "弦乐",
    "制作团队", "打击乐", "采样", "音效", "人声", "合成器", "录音师", "混音师", "编曲师",
    "出品", "发行", "企划", "统筹", "后期", "音乐总监", "lyrics", "music", "composer",
)
PURE_MUSIC_PHRASES = (
    "纯音乐，请欣赏",
    "纯音乐, 请欣赏",
    "纯音乐 请欣赏",
    "此歌曲为没有填词的纯音乐",
    "instrumental",
)


@dataclass(slots=True)
class ParsedLRC:
    synced: str
    plain: str
    is_instrumental: bool
    has_valid_timestamps: bool
    warnings: list[str] = field(default_factory=list)
    original_text: str = ""


@dataclass(slots=True)
class CleanseResult:
    status: str
    original_text: str
    cleaned_text: Optional[str]
    reason: Optional[str] = None
    parsed: Optional[ParsedLRC] = None


def normalize_name(text: str) -> str:
    value = unicodedata.normalize("NFKC", text.strip().lower())
    cyrillic_map = {"ё": "е", "і": "и", "ї": "и", "є": "е", "ґ": "г"}
    for old, new in cyrillic_map.items():
        value = value.replace(old, new)
    replacements = {
        "（": "(", "）": ")", "【": "[", "】": "]", "：": ":", "。": ".", "，": ",",
        "！": "!", "？": "?", "＆": "&", "／": "/", "；": ";",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = "".join(ch for ch in value if unicodedata.category(ch)[0] not in ("C", "Z") or ch == " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def read_text_any(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", text))


def _is_credit(text: str) -> bool:
    value = text.strip().lower()
    for key in CREDIT_KEYWORDS:
        if value.startswith(key.lower() + ":") or value.startswith(key.lower() + "："):
            return True
    return False


def parse_lrc_text(text: str, *, remove_translations: bool = True) -> ParsedLRC:
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    warnings: list[str] = []
    if not TIMESTAMP_RE.search(raw):
        warnings.append("no_valid_timestamps")
        return ParsedLRC("", "", False, False, warnings=warnings, original_text=text)

    synced_lines: list[str] = []
    plain_lines: list[str] = []
    started = False
    prev_timestamp: Optional[str] = None
    is_instrumental = False

    for line in raw.splitlines():
        stripped = line.strip()
        if not started:
            if TIMESTAMP_RE.match(stripped):
                started = True
            else:
                continue
        if not stripped:
            synced_lines.append("")
            plain_lines.append("")
            prev_timestamp = None
            continue
        if HEADER_TAG_RE.match(stripped):
            prev_timestamp = None
            continue
        timestamp_match = EXTENDED_TIMESTAMP_RE.match(stripped)
        if timestamp_match:
            current_timestamp = timestamp_match.group(0)
            content = stripped[len(current_timestamp):].strip()
            if content and any(phrase.lower() in content.lower() for phrase in PURE_MUSIC_PHRASES):
                is_instrumental = True
                prev_timestamp = None
                continue
            if content and _is_credit(content):
                prev_timestamp = None
                continue
            if remove_translations and prev_timestamp == current_timestamp and _contains_cjk(content):
                continue
            synced_lines.append(f"{current_timestamp}{content}" if content else current_timestamp)
            plain_lines.append(content)
            prev_timestamp = current_timestamp
            continue
        synced_lines.append(stripped)
        plain_lines.append(stripped)
        prev_timestamp = None

    while plain_lines and not plain_lines[0].strip():
        plain_lines.pop(0)
    while plain_lines and not plain_lines[-1].strip():
        plain_lines.pop()
    synced = "\n".join(synced_lines).strip("\n")
    plain = "\n".join(plain_lines).strip("\n")
    return ParsedLRC(
        synced=synced,
        plain=plain,
        is_instrumental=is_instrumental,
        has_valid_timestamps=True,
        warnings=warnings,
        original_text=text,
    )


def parse_lrc_file(path: Path, *, remove_translations: bool = True) -> ParsedLRC:
    try:
        text = read_text_any(path)
    except Exception as exc:
        log_error(f"failed to read LRC {path}: {exc}")
        return ParsedLRC("", "", False, False, warnings=["read_failed"], original_text="")
    return parse_lrc_text(text, remove_translations=remove_translations)


def cleanse_lrc_file(path: Path, *, write: bool = False, remove_translations: bool = True) -> CleanseResult:
    parsed = parse_lrc_file(path, remove_translations=remove_translations)
    original = parsed.original_text
    if not parsed.has_valid_timestamps:
        return CleanseResult("invalid", original, None, reason="no_valid_timestamps", parsed=parsed)
    cleaned = parsed.synced
    if original.strip() and not cleaned.strip() and not parsed.is_instrumental:
        return CleanseResult("invalid", original, None, reason="empty_after_cleanse", parsed=parsed)
    if write and cleaned != original:
        try:
            path.write_text(cleaned, encoding="utf-8")
        except Exception as exc:
            return CleanseResult("failed", original, cleaned, reason=str(exc), parsed=parsed)
        return CleanseResult("updated", original, cleaned, parsed=parsed)
    if cleaned == original:
        return CleanseResult("unchanged", original, cleaned, parsed=parsed)
    return CleanseResult("updated", original, cleaned, parsed=parsed)
