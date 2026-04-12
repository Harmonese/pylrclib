from __future__ import annotations

import json
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeLRCLIBHandler(BaseHTTPRequestHandler):
    state = {
        'cache_payload': None,
        'external_payload': None,
        'search_payload': None,
        'by_id_payloads': {},
        'publish_requests': [],
        'publish_status': 201,
        'retry_after': None,
    }

    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        if self.state.get('retry_after') is not None:
            self.send_header('Retry-After', str(self.state['retry_after']))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith('/api/get-cached'):
            payload = self.state.get('cache_payload')
            if payload is None:
                self._send_json(404, {'detail': 'not found'})
            else:
                self._send_json(200, payload)
            return
        if path.startswith('/api/get/'):
            record_id = path.rsplit('/', 1)[-1]
            payload = self.state.get('by_id_payloads', {}).get(record_id)
            if payload is None:
                self._send_json(404, {'detail': 'not found'})
            else:
                self._send_json(200, payload)
            return
        if path.startswith('/api/get'):
            payload = self.state.get('external_payload')
            if payload is None:
                self._send_json(404, {'detail': 'not found'})
            else:
                self._send_json(200, payload)
            return
        if path.startswith('/api/search'):
            payload = self.state.get('search_payload')
            if callable(payload):
                payload = payload(parse_qs(parsed.query))
            if payload is None:
                self._send_json(404, {'detail': 'not found'})
            else:
                self._send_json(200, payload)
            return
        self._send_json(404, {'detail': 'unknown'})

    def do_POST(self):
        if self.path == '/api/request-challenge':
            self._send_json(200, {'prefix': 'test', 'target': 'f' * 64})
            return
        if self.path == '/api/publish':
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or b'{}')
            self.state['publish_requests'].append({
                'headers': dict(self.headers),
                'payload': payload,
            })
            status = self.state.get('publish_status', 201)
            if status == 201:
                self._send_json(201, {'ok': True})
            else:
                self._send_json(status, {'ok': False})
            return
        self._send_json(404, {'detail': 'unknown'})

    def log_message(self, format, *args):
        return


@contextmanager
def fake_lrclib_server(cache_payload=None, external_payload=None, search_payload=None, by_id_payloads=None, publish_status=201, retry_after=None):
    FakeLRCLIBHandler.state = {
        'cache_payload': cache_payload,
        'external_payload': external_payload,
        'search_payload': search_payload,
        'by_id_payloads': by_id_payloads or {},
        'publish_requests': [],
        'publish_status': publish_status,
        'retry_after': retry_after,
    }
    server = ThreadingHTTPServer(('127.0.0.1', 0), FakeLRCLIBHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}/api', FakeLRCLIBHandler.state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def lrclib_server():
    with fake_lrclib_server() as value:
        yield value
