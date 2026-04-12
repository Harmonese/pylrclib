from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(slots=True)
class LyricsRecord:
    plain: str
    synced: str
    instrumental: bool
    duration: Optional[int] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "LyricsRecord":
        plain = (data.get("plainLyrics") or "").strip("\n")
        synced = (data.get("syncedLyrics") or "").strip("\n")
        instrumental = bool(data.get("instrumental", False))
        if not plain.strip() and not synced.strip() and not instrumental:
            instrumental = True
        duration = None
        value = data.get("duration")
        if value is not None:
            try:
                duration = int(round(float(value)))
            except (TypeError, ValueError):
                duration = None
        return cls(plain=plain, synced=synced, instrumental=instrumental, duration=duration)


@dataclass(slots=True)
class LookupResult:
    record: Optional[LyricsRecord]
    duration_diff: Optional[int]
    duration_ok: bool
    source: str


@dataclass(slots=True)
class LyricsBundle:
    kind: str
    plain: str = ""
    synced: str = ""
    instrumental: bool = False
    plain_path: Optional[Path] = None
    synced_path: Optional[Path] = None
    warnings: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.instrumental and not self.plain.strip() and not self.synced.strip()

    @property
    def has_plain(self) -> bool:
        return bool(self.plain.strip())

    @property
    def has_synced(self) -> bool:
        return bool(self.synced.strip())

    @classmethod
    def empty(cls) -> "LyricsBundle":
        return cls(kind="empty")
