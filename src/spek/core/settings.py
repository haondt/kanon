from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel

from spek.core.yaml_utils import load_yaml


class SourceSpec(BaseModel):
    path: str
    url: str | None = None
    ref: str | None = None


class GlobalSettings(BaseModel):
    sources: dict[str, SourceSpec] = {}


def load_global_settings() -> GlobalSettings:
    settings_path = Path.home() / ".spek" / "settings.yaml"
    if not settings_path.exists():
        return GlobalSettings()
    return load_yaml(settings_path, GlobalSettings)
