from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel

from spek.core.settings import SourceSpec
from spek.core.yaml_utils import load_yaml, save_yaml

CONFIG_FILE = ".spek/spek.yaml"
MODULES_DIR = ".spek/modules"
STANCES_DIR = ".spek/stances"
LOCAL_MODULES_DIR = ".spek/local/modules"
LOCAL_STANCES_DIR = ".spek/local/stances"

SPEK_NAMESPACE = "spek"


class SpekMeta(BaseModel):
    spek_version: str
    spek_sha: str
    integrations: list[str]
    profile: str | None = None


class SpekConfig(BaseModel):
    meta: SpekMeta
    modules: list[str] = []
    stances: list[str] = []
    local_modules: list[str] = []
    local_stances: list[str] = []
    sources: dict[str, SourceSpec] = {}

    @classmethod
    def load(cls, path: Path) -> SpekConfig:
        return load_yaml(path, cls)

    def save(self, path: Path) -> None:
        save_yaml(self, path)
