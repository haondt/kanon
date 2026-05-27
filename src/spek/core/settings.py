from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel

from spek.core.yaml_utils import load_yaml, save_yaml
from spek.core.config import SpekEnv


class GlobalSettings(BaseModel):
    _current: ClassVar[GlobalSettings | None] = None
    _path: ClassVar[Path | None] = None

    sources: dict[str, str] = {}

    @classmethod
    def reset(cls) -> None:
        cls._current = None
        cls._path = None

    @classmethod
    def initialize(cls) -> GlobalSettings:
        path = SpekEnv.instance().settings_path
        cls._path = path
        if not path.exists():
            cls._current = cls()
        else:
            cls._current = load_yaml(path, cls)
        return cls._current

    @classmethod
    def instance(cls) -> GlobalSettings:
        if cls._current is None:
            return cls.initialize()
        return cls._current

    def save(self) -> None:
        path = GlobalSettings._path or SpekEnv.instance().settings_path
        path.parent.mkdir(parents=True, exist_ok=True)
        save_yaml(self, path)
