from __future__ import annotations

import sys

from .i18n import get_text


def log_info(message: str) -> None:
    print(f"[{get_text('log.info')}] {message}")


def log_warn(message: str) -> None:
    print(f"[{get_text('log.warn')}] {message}", file=sys.stderr)


def log_error(message: str) -> None:
    print(f"[{get_text('log.error')}] {message}", file=sys.stderr)


def log_debug(message: str) -> None:
    print(f"[{get_text('log.debug')}] {message}", file=sys.stderr)
