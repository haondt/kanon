from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILE = ".spek/spek.yaml"
MODULES_DIR = ".spek/modules"
STANCES_DIR = ".spek/stances"
LOCAL_MODULES_DIR = ".spek/local/modules"
LOCAL_STANCES_DIR = ".spek/local/stances"


@dataclass
class SpekMeta:
    spek_version: str
    spek_sha: str
    ai_tool: str
    profile: str | None = None


@dataclass
class SpekConfig:
    meta: SpekMeta
    modules: list[str] = field(default_factory=list)
    stances: list[str] = field(default_factory=list)
    local_modules: list[str] = field(default_factory=list)
    local_stances: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "SpekConfig":
        data = yaml.safe_load(path.read_text())
        meta = SpekMeta(
            spek_version=data["meta"]["spek_version"],
            spek_sha=data["meta"]["spek_sha"],
            ai_tool=data["meta"]["ai_tool"],
            profile=data["meta"].get("profile"),
        )
        return cls(
            meta=meta,
            modules=data.get("modules", []),
            stances=data.get("stances", []),
            local_modules=data.get("local_modules", []),
            local_stances=data.get("local_stances", []),
        )

    def save(self, path: Path) -> None:
        meta: dict = {
            "spek_version": self.meta.spek_version,
            "spek_sha": self.meta.spek_sha,
            "ai_tool": self.meta.ai_tool,
        }
        if self.meta.profile:
            meta["profile"] = self.meta.profile
        data: dict = {"meta": meta, "modules": self.modules}
        if self.stances:
            data["stances"] = self.stances
        if self.local_modules:
            data["local_modules"] = self.local_modules
        if self.local_stances:
            data["local_stances"] = self.local_stances
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
