"""pylrclib package."""

import re
from pathlib import Path

__all__ = ["__version__"]


def _get_version() -> str:
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject.exists():
        match = re.search(r'^\s*version\s*=\s*"([^"]+)"', pyproject.read_text(), re.MULTILINE)
        if match:
            return match.group(1)
    try:
        from importlib.metadata import PackageNotFoundError, version as _package_version
        return _package_version("pylrclib-cli")
    except (ImportError, PackageNotFoundError):
        pass
    return "0.0.0"


__version__ = _get_version()
