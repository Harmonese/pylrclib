from __future__ import annotations

import time
from typing import Any, Optional

import requests
from requests import RequestException

from ..config import CommonOptions
from ..logging_utils import log_warn
from ..models import TrackMeta
from .http import http_request_json
from .pow import solve_pow
from .retry import calculate_backoff, is_retryable_status, parse_retry_after


def request_publish_token(options: CommonOptions) -> Optional[str]:
    data = http_request_json(
        options,
        method="POST",
        url=f"{options.lrclib_base}/request-challenge",
        label="request publish challenge",
        treat_404_as_none=False,
    )
    if not data:
        return None
    prefix = data.get("prefix")
    target = data.get("target")
    if not prefix or not target:
        return None
    nonce = solve_pow(prefix, target)
    return f"{prefix}:{nonce}"


def build_publish_payload(meta: TrackMeta, plain: Optional[str], synced: Optional[str], *, instrumental: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "trackName": meta.track,
        "artistName": meta.artist,
        "albumName": meta.album,
        "duration": meta.duration,
    }
    if instrumental:
        return payload
    plain_text = (plain or "").strip()
    synced_text = (synced or "").strip()
    if plain_text:
        payload["plainLyrics"] = plain_text
    if synced_text:
        payload["syncedLyrics"] = synced_text
    return payload


def publish_with_retry(options: CommonOptions, meta: TrackMeta, payload: dict[str, Any], label: str) -> bool:
    url = f"{options.lrclib_base}/publish"
    retries = options.max_http_retries
    for attempt in range(1, retries + 1):
        token = request_publish_token(options)
        if not token:
            if attempt == retries:
                return False
            delay = calculate_backoff(attempt)
            time.sleep(delay)
            continue
        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "User-Agent": options.user_agent,
                    "Content-Type": "application/json",
                    "X-Publish-Token": token,
                },
                timeout=30,
            )
        except RequestException as exc:
            if attempt == retries:
                log_warn(f"{label} failed after {attempt} attempts: {exc}")
                return False
            delay = calculate_backoff(attempt)
            time.sleep(delay)
            continue
        if response.status_code == 201:
            return True
        if is_retryable_status(response.status_code):
            if attempt == retries:
                return False
            delay = parse_retry_after(response.headers.get("Retry-After")) or calculate_backoff(attempt)
            time.sleep(delay)
            continue
        log_warn(f"{label} failed with HTTP {response.status_code}: {response.text[:200]}")
        return False
    return False
