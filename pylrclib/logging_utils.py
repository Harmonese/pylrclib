from __future__ import annotations

import sys


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_warn(message: str) -> None:
    print(f"[WARN] {message}", file=sys.stderr)


def log_error(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)


def log_debug(message: str) -> None:
    print(f"[DEBUG] {message}", file=sys.stderr)
