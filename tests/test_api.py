from pylrclib.api.client import ApiClient
from pylrclib.config import CommonOptions
from pylrclib.models import TrackMeta


class DummyResponse:
    pass


def test_lookup_duration_mismatch(monkeypatch):
    def fake_http_request_json(*args, **kwargs):
        return {
            "plainLyrics": "hello",
            "syncedLyrics": "[00:00.00]hello",
            "instrumental": False,
            "duration": 210,
        }

    monkeypatch.setattr("pylrclib.api.client.http_request_json", fake_http_request_json)
    client = ApiClient(CommonOptions(lang="en_US", preview_lines=10, max_http_retries=1, user_agent="ua", lrclib_base="http://x"))
    meta = TrackMeta(path=None, track="Song", artist="Artist", album="Album", duration=180)
    result = client.get_cached(meta)
    assert result.record is not None
    assert result.duration_ok is False
    assert result.duration_diff == 30
