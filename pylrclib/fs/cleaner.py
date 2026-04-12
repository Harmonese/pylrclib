from __future__ import annotations

from pathlib import Path

from ..logging_utils import log_warn


def cleanup_empty_dirs(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        return
    directories = sorted((path for path in root.rglob("*") if path.is_dir()), key=lambda item: len(item.parts), reverse=True)
    for directory in directories:
        try:
            if not any(directory.iterdir()):
                directory.rmdir()
        except OSError as exc:
            log_warn(f"failed to delete empty directory {directory}: {exc}")
