from __future__ import annotations

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
            method="GET",
            url=f"{self.options.lrclib_base}/{endpoint}",
            label=source,
            params={
                "track_name": meta.track,
                "artist_name": meta.artist,
                "album_name": meta.album,
                "duration": meta.duration,
            },
        )
        if not data:
            return LookupResult(record=None, duration_diff=None, duration_ok=False, source=source)
        record = LyricsRecord.from_api(data)
        diff = None
        ok = True
        if record.duration is not None:
            diff = abs(record.duration - meta.duration)
            ok = diff <= 2
        return LookupResult(record=record, duration_diff=diff, duration_ok=ok, source=source)

    def get_cached(self, meta: TrackMeta) -> LookupResult:
        return self._lookup(meta, "get-cached", "cache")

    def get_external(self, meta: TrackMeta) -> LookupResult:
        return self._lookup(meta, "get", "external")

    def upload_lyrics(self, meta: TrackMeta, plain: str, synced: str) -> bool:
        payload = build_publish_payload(meta, plain, synced, instrumental=False)
        return publish_with_retry(self.options, meta, payload, "upload lyrics")

    def upload_instrumental(self, meta: TrackMeta) -> bool:
        payload = build_publish_payload(meta, None, None, instrumental=True)
        return publish_with_retry(self.options, meta, payload, "upload instrumental")
