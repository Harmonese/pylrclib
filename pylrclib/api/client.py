from __future__ import annotations

from typing import Any

from ..config import CommonOptions
from ..models import LookupResult, LyricsRecord, TrackMeta
from .http import http_request_json
from .publish import build_publish_payload, publish_with_retry


class ApiClient:
    def __init__(self, options: CommonOptions) -> None:
        self.options = options

    def _lookup(self, meta: TrackMeta, endpoint: str, source: str) -> LookupResult:
        data = http_request_json(
            self.options,
            method='GET',
            url=f'{self.options.lrclib_base}/{endpoint}',
            label=source,
            params={
                'track_name': meta.track,
                'artist_name': meta.artist,
                'album_name': meta.album,
                'duration': meta.duration,
            },
        )
        if not data:
            return LookupResult(record=None, duration_diff=None, duration_ok=False, source=source)
        record = LyricsRecord.from_api(data)
        diff = None
        ok = True
        if record.duration is not None and meta.duration > 0:
            diff = abs(record.duration - meta.duration)
            ok = diff <= 2
        return LookupResult(record=record, duration_diff=diff, duration_ok=ok, source=source)

    def get_cached(self, meta: TrackMeta) -> LookupResult:
        return self._lookup(meta, 'get-cached', 'cache')

    def get_external(self, meta: TrackMeta) -> LookupResult:
        return self._lookup(meta, 'get', 'external')

    def get_by_id(self, lrclib_id: int) -> LyricsRecord | None:
        data = http_request_json(
            self.options,
            method='GET',
            url=f'{self.options.lrclib_base}/get/{int(lrclib_id)}',
            label=f'get_by_id:{lrclib_id}',
            treat_404_as_none=True,
        )
        if not isinstance(data, dict):
            return None
        return LyricsRecord.from_api(data)

    def search(
        self,
        *,
        query: str | None = None,
        track_name: str | None = None,
        artist_name: str | None = None,
        album_name: str | None = None,
    ) -> list[LyricsRecord]:
        if not query and not track_name:
            raise ValueError('Either query or track_name is required for search')
        data = http_request_json(
            self.options,
            method='GET',
            url=f'{self.options.lrclib_base}/search',
            label='search',
            params={
                'q': query,
                'track_name': track_name,
                'artist_name': artist_name,
                'album_name': album_name,
            },
            treat_404_as_none=True,
        )
        if data is None:
            return []
        if isinstance(data, list):
            return [LyricsRecord.from_api(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [LyricsRecord.from_api(data)]
        return []

    def upload_lyrics(self, meta: TrackMeta, plain: str, synced: str) -> bool:
        payload = build_publish_payload(meta, plain, synced, instrumental=False)
        return publish_with_retry(self.options, meta, payload, 'upload lyrics')

    def upload_instrumental(self, meta: TrackMeta) -> bool:
        payload = build_publish_payload(meta, None, None, instrumental=True)
        return publish_with_retry(self.options, meta, payload, 'upload instrumental')
