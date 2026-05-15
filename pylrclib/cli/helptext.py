from __future__ import annotations

import argparse

from ..config import (
    DEFAULT_USER_AGENT,
    LRCLIB_BASE,
    MAX_HTTP_RETRIES_DEFAULT,
    PREVIEW_LINES_DEFAULT,
)
from ..i18n import get_text


class RichHelpFormatter(argparse.RawTextHelpFormatter):
    """Readable help formatter with preserved line breaks for examples."""


def with_default(text: str, default: str) -> str:
    return f"{text} {get_text('cli.default_template', default=default)}"


def common_network_help() -> dict[str, str]:
    return {
        "preview_lines": with_default(
            get_text("cli.help.preview_lines"),
            str(PREVIEW_LINES_DEFAULT),
        ),
        "max_retries": with_default(
            get_text("cli.help.max_retries"),
            str(MAX_HTTP_RETRIES_DEFAULT),
        ),
        "user_agent": with_default(
            get_text("cli.help.user_agent"),
            DEFAULT_USER_AGENT,
        ),
        "api_base": with_default(
            get_text("cli.help.api_base"),
            LRCLIB_BASE,
        ),
        "yes": with_default(
            get_text("cli.help.yes"),
            "disabled",
        ),
        "non_interactive": with_default(
            get_text("cli.help.non_interactive"),
            "disabled",
        ),
    }
