from __future__ import annotations

import argparse

from ..config import (
    DEFAULT_USER_AGENT,
    LRCLIB_BASE,
    MAX_HTTP_RETRIES_DEFAULT,
    PREVIEW_LINES_DEFAULT,
)


class RichHelpFormatter(argparse.RawTextHelpFormatter):
    """Readable help formatter with preserved line breaks for examples."""


def with_default(text: str, default: str) -> str:
    return f"{text} Default: {default}."


def common_network_help() -> dict[str, str]:
    return {
        "preview_lines": with_default(
            "How many lyric lines to preview when showing plain or synced lyrics.",
            str(PREVIEW_LINES_DEFAULT),
        ),
        "max_retries": with_default(
            "Maximum HTTP retry attempts for retryable LRCLIB requests.",
            str(MAX_HTTP_RETRIES_DEFAULT),
        ),
        "user_agent": with_default(
            "HTTP User-Agent header sent to LRCLIB.",
            DEFAULT_USER_AGENT,
        ),
        "api_base": with_default(
            "Base LRCLIB API URL.",
            LRCLIB_BASE,
        ),
        "yes": with_default(
            "Assume yes for confirmation prompts that would otherwise ask before writing or publishing.",
            "disabled",
        ),
        "non_interactive": with_default(
            "Disable interactive prompts and use safe automatic decisions.",
            "disabled",
        ),
    }
