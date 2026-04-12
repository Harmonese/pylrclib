from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_YAML_EXTENSIONS
from .models import TrackMeta, YamlTrackMeta


@dataclass(slots=True)
class InputItem:
    original_meta: TrackMeta | YamlTrackMeta
    api_meta: TrackMeta
    source_kind: str

    @property
    def label(self) -> str:
        return f'[{self.source_kind}] {self.api_meta}'


def discover_inputs(tracks_dir: Path) -> list[InputItem]:
    items: list[InputItem] = []
    if tracks_dir.exists():
        for path in sorted(tracks_dir.rglob('*')):
            if path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                meta = TrackMeta.from_audio_file(path)
                if meta:
                    items.append(InputItem(original_meta=meta, api_meta=meta, source_kind='audio'))
            elif path.suffix.lower() in SUPPORTED_YAML_EXTENSIONS:
                meta = YamlTrackMeta.from_yaml_file(path)
                if meta:
                    items.append(InputItem(original_meta=meta, api_meta=TrackMeta.from_yaml(meta), source_kind='yaml'))
    return items
