from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from ..logging_utils import log_warn


def move_with_dedup(src: Path, dst_dir: Path, new_name: Optional[str] = None) -> Optional[Path]:
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        target = dst_dir / (f"{new_name}{src.suffix}" if new_name else src.name)
        src_resolved = src.resolve()
        target_resolved = target.resolve() if target.exists() else target
        if src_resolved == target_resolved:
            return src
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            counter = 1
            while True:
                candidate = dst_dir / f"{stem}_dup{counter}{suffix}"
                if not candidate.exists():
                    target = candidate
                    break
                counter += 1
        shutil.move(str(src), str(target))
        return target
    except Exception as exc:
        log_warn(f"failed to move {src} -> {dst_dir}: {exc}")
        return None
