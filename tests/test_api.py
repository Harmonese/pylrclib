from pylrclib.api.client import ApiClient
from pylrclib.config import CommonOptions
from pylrclib.models import TrackMeta


def _client() -> ApiClient:
    return ApiClient(CommonOptions(lang='en_US', preview_lines=10, max_http_retries=1, user_agent='ua', lrclib_base='http://x'))


def test_lookup_duration_mismatch(monkeypatch):
    def fake_http_request_json(*args, **kwargs):
        return {
            'plainLyrics': 'hello',
            'syncedLyrics': '[00:00.00]hello',
            'instrumental': False,
            'duration': 210,
        }

    monkeypatch.setattr('pylrclib.api.client.http_request_json', fake_http_request_json)
    client = _client()
    meta = TrackMeta(path=None, track='Song', artist='Artist', album='Album', duration=180)
    result = client.get_cached(meta)
    assert result.record is not None
    assert result.duration_ok is False
    assert result.duration_diff == 30


def test_search_records(monkeypatch):
    def fake_http_request_json(*args, **kwargs):
        return [
            {
                'id': 42,
                'trackName': 'Song',
                'artistName': 'Artist',
                'albumName': 'Album',
                'duration': 180,
                'plainLyrics': 'hello',
                'syncedLyrics': '[00:00.00]hello',
                'instrumental': False,
            }
        ]

    monkeypatch.setattr('pylrclib.api.client.http_request_json', fake_http_request_json)
    results = _client().search(query='song')
    assert len(results) == 1
    assert results[0].lrclib_id == 42
    assert results[0].track_name == 'Song'


def test_get_by_id(monkeypatch):
    def fake_http_request_json(*args, **kwargs):
        return {
            'id': 7,
            'trackName': 'Song',
            'artistName': 'Artist',
            'albumName': 'Album',
            'duration': 180,
            'plainLyrics': 'hello',
            'syncedLyrics': '',
            'instrumental': False,
        }

    monkeypatch.setattr('pylrclib.api.client.http_request_json', fake_http_request_json)
    record = _client().get_by_id(7)
    assert record is not None
    assert record.lrclib_id == 7
    assert record.artist_name == 'Artist'
