from __future__ import annotations

import os
from typing import Optional

_CURRENT_LOCALE = "en_US"


def setup_i18n(locale: Optional[str] = None) -> str:
    global _CURRENT_LOCALE
    value = locale or os.getenv("PYLRCLIB_LANG") or "auto"
    if value == "auto":
        lang = os.getenv("LANG", "en_US")
        if lang.lower().startswith("zh"):
            _CURRENT_LOCALE = "zh_CN"
        else:
            _CURRENT_LOCALE = "en_US"
    else:
        _CURRENT_LOCALE = value
    return _CURRENT_LOCALE


def get_locale() -> str:
    return _CURRENT_LOCALE


def get_text(message: str) -> str:
    return message
