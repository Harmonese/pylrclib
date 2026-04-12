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
    lrclib_id: Optional[int] = None
    track_name: str = ''
    artist_name: str = ''
    album_name: str = ''

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'LyricsRecord':
        plain = (data.get('plainLyrics') or '').strip('\n')
        synced = (data.get('syncedLyrics') or '').strip('\n')
        instrumental = bool(data.get('instrumental', False))
        if not plain.strip() and not synced.strip() and not instrumental:
            instrumental = True
        duration = None
        value = data.get('duration')
        if value is not None:
            try:
                duration = int(round(float(value)))
            except (TypeError, ValueError):
                duration = None
        lrclib_id = None
        raw_id = data.get('id')
        if raw_id is not None:
            try:
                lrclib_id = int(raw_id)
            except (TypeError, ValueError):
                lrclib_id = None
        track_name = str(data.get('trackName') or data.get('name') or data.get('track_name') or '').strip()
        artist_name = str(data.get('artistName') or data.get('artist_name') or '').strip()
        album_name = str(data.get('albumName') or data.get('album_name') or '').strip()
        return cls(
            plain=plain,
            synced=synced,
            instrumental=instrumental,
            duration=duration,
            lrclib_id=lrclib_id,
            track_name=track_name,
            artist_name=artist_name,
            album_name=album_name,
        )

    @property
    def label(self) -> str:
        prefix = f'#{self.lrclib_id} ' if self.lrclib_id is not None else ''
        core = ' - '.join(part for part in [self.artist_name, self.track_name] if part)
        if self.album_name:
            core = f'{core} [{self.album_name}]' if core else self.album_name
        if self.duration is not None:
            core = f'{core} ({self.duration}s)' if core else f'({self.duration}s)'
        return (prefix + core).strip() or prefix.rstrip() or '<unknown>'


@dataclass(slots=True)
class LookupResult:
    record: Optional[LyricsRecord]
    duration_diff: Optional[int]
    duration_ok: bool
    source: str


@dataclass(slots=True)
class LyricsBundle:
    kind: str
    plain: str = ''
    synced: str = ''
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
    def empty(cls) -> 'LyricsBundle':
        return cls(kind='empty')
