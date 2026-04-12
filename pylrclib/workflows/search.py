from __future__ import annotations

import json

from ..api import ApiClient
from ..config import CommonOptions
from ..logging_utils import log_warn
from ..models import LyricsRecord
from .up import preview


def _record_to_dict(record: LyricsRecord) -> dict[str, object]:
    return {
        'id': record.lrclib_id,
        'trackName': record.track_name,
        'artistName': record.artist_name,
        'albumName': record.album_name,
        'duration': record.duration,
        'instrumental': record.instrumental,
        'plainLyrics': record.plain,
        'syncedLyrics': record.synced,
    }


def run_search(
    options: CommonOptions,
    *,
    lrclib_id: int | None,
    query: str | None,
    title: str | None,
    artist: str | None,
    album: str | None,
    limit: int | None,
    as_json: bool,
) -> int:
    client = ApiClient(options)
    if lrclib_id is not None:
        record = client.get_by_id(lrclib_id)
        records = [record] if record is not None else []
    else:
        records = client.search(query=query, track_name=title, artist_name=artist, album_name=album)
        if limit is not None and limit >= 0:
            records = records[:limit]
    if as_json:
        print(json.dumps([_record_to_dict(r) for r in records], ensure_ascii=False, indent=2))
        return 0
    if not records:
        log_warn('no search results')
        return 0
    for idx, record in enumerate(records, 1):
        print(f'[{idx}] {record.label}')
        preview('plainLyrics', record.plain, options.preview_lines)
        preview('syncedLyrics', record.synced, options.preview_lines)
    return 0
