from __future__ import annotations

import time
from typing import Any, Optional

import requests
from requests import RequestException

from ..config import CommonOptions
from ..i18n import get_text
from ..logging_utils import log_warn
from .retry import calculate_backoff, is_retryable_status, parse_retry_after


def http_request_json(
    options: CommonOptions,
    method: str,
    url: str,
    label: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json_data: Optional[dict[str, Any]] = None,
    timeout: int = 20,
    max_retries: Optional[int] = None,
    treat_404_as_none: bool = True,
) -> Any:
    retries = max_retries if max_retries is not None else options.max_http_retries
    for attempt in range(1, retries + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=timeout,
                headers={"User-Agent": options.user_agent},
            )
        except RequestException as exc:
            if attempt == retries:
                log_warn(get_text("api.request_failed", label=label, attempts=attempt, exc=exc))
                return None
            delay = calculate_backoff(attempt)
            log_warn(get_text("api.request_error", label=label, attempt=attempt, retries=retries, exc=exc, delay=delay))
            time.sleep(delay)
            continue

        if response.status_code == 404 and treat_404_as_none:
            return None
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                log_warn(get_text("api.invalid_json", label=label, text=response.text[:200]))
                return None
        if is_retryable_status(response.status_code):
            if attempt == retries:
                log_warn(get_text("api.http_fail_final", label=label, attempts=attempt, status=response.status_code, text=response.text[:200]))
                return None
            delay = parse_retry_after(response.headers.get("Retry-After")) or calculate_backoff(attempt)
            log_warn(get_text("api.http_fail_retry", label=label, status=response.status_code, delay=delay))
            time.sleep(delay)
            continue
        log_warn(get_text("api.http_fail_final", label=label, attempts=attempt, status=response.status_code, text=response.text[:200]))
        return None
    return None
