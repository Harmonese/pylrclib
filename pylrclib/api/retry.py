from __future__ import annotations

import random
from email.utils import parsedate_to_datetime
from typing import Optional

RETRYABLE_STATUSES = {408, 425, 429, 500, 502, 503, 504}


def calculate_backoff(attempt: int, base: float = 1.0, max_delay: float = 30.0) -> float:
    return min(base * (2 ** (attempt - 1)) + random.uniform(0, 1), max_delay)


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
            return max(0.0, (dt - dt.now(dt.tzinfo)).total_seconds())
        except Exception:
            return None


def is_retryable_status(status: int) -> bool:
    return status in RETRYABLE_STATUSES
