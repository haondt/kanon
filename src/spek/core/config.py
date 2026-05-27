from __future__ import annotations

import importlib.resources
import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from collections.abc import Sequence
from typing import Any, ClassVar
from pydantic import BaseModel, Field

from spek.core.yaml_utils import load_yaml, save_yaml
from spek.core.utils import resolve_path

from functools import cached_property

PROJECT_SPEK_DIR = ".spek"
CONFIG_FILE = "spek.yaml"

SYNCED_MODULES_DIR = "modules"
SYNCED_STANCES_DIR = "stances"

PROJECT_MODULES_DIR = "project/modules"
PROJECT_PROFILES_DIR = "project/profiles"
PROJECT_STANCES_DIR = "project/stances"
PROJECT_REFS_DIR = "project/references"

SPEK_SOURCE = "spek"
PROJECT_SOURCE = "project"

SOURCED_RESOURCE_SOURCE_SEP = "::"
SOURCED_MODULES_DIR = "specs"
SOURCED_REFS_DIR = "references"
SOURCED_PROFILES_DIR = "profiles"
SOURCED_STANCES_DIR = "stances"

class OutputType(StrEnum):
    RULE = "rule"
    SKILL = "skill"


class Integration(StrEnum):
    CLAUDE = "claude"
    WINDSURF = "windsurf"

@dataclass
class IntegrationSpecificRule:
    path: str
    content: str
    frontmatter: dict[str, Any] = Field(default_factory=dict)

AI_TOOL_OUTPUT_DIRS: dict[Integration, dict[OutputType, str]] = {
    Integration.CLAUDE: {
        OutputType.RULE: ".claude/rules",
        OutputType.SKILL: ".claude/skills",
    },
    Integration.WINDSURF: {
        OutputType.RULE: ".windsurf/rules",
        OutputType.SKILL: ".windsurf/workflows",
    },
}

AI_TOOL_SETTINGS_FILES: dict[Integration, str] = {
    Integration.CLAUDE: ".claude/settings.json",
}

AI_TOOL_SPECIFIC_RULES: dict[Integration, list[IntegrationSpecificRule]] = {
    Integration.WINDSURF: [
        IntegrationSpecificRule(
            path="windsurf-rules",
            frontmatter={"trigger": "always_on"},
            content="""## Project structure
- CRITICAL: The first action in every conversation is reading @.spek/STRUCTURE.md. Do not respond to the user, write any files or plan any actions until this is complete.
- When running shell commands, prefer using the bash tool over interactive shell execution for better syntax highlighting in the chat window.""",
        )
    ]
}

class SpekEnv:
    """Environment-sourced configuration singleton. Values are lazily cached per instance."""
    _instance: ClassVar[SpekEnv | None] = None

    @classmethod
    def instance(cls) -> SpekEnv:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @cached_property
    def repo_path(self) -> Path:
        if val := os.environ.get("SPEK_REPO_PATH"):
            return Path(val)
        pkg_path = Path(importlib.resources.files("spek").__str__())
        candidate = pkg_path
        while candidate != candidate.parent:
            if (candidate / ".git").exists():
                return candidate
            candidate = candidate.parent
        raise RuntimeError("Could not locate spek repo root (no .git found)")

    @cached_property
    def settings_path(self) -> Path:
        if val := os.environ.get("SPEK_SETTINGS_PATH"):
            return Path(val)
        return Path.home() / ".spek" / "settings.yaml"



class SpekMeta(BaseModel):
    spek_version: str
    spek_sha: str
    integrations: list[Integration]
    profile: str | None = None


class SpekConfig(BaseModel):
    _current: ClassVar[SpekConfig | None] = None
    _root: ClassVar[Path | None] = None

    meta: SpekMeta
    modules: list[str] = []
    stances: list[str] = []
    local_modules: list[str] = []
    local_stances: list[str] = []
    sources: dict[str, str] = {}

    @property
    def stances_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.stances]

    @property
    def modules_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.modules]

    @classmethod
    def initialize(cls, project_root: Path | str | None = None) -> None:
        root = resolve_path(project_root) / PROJECT_SPEK_DIR
        cls._root = root
        cls._current = None
        config_path = root / CONFIG_FILE
        if not config_path.exists():
            return None
        cls._current = load_yaml(config_path, cls)

    @classmethod
    def instance(cls) -> SpekConfig:
        if cls._current is None:
            raise RuntimeError("No spek.yaml found in the current directory.")
        return cls._current

    @classmethod
    def get(cls) -> SpekConfig | None:
        return cls._current

    @classmethod
    def root(cls) -> Path:
        """Path to projects .spek directory"""
        if cls._root is None:
            raise RuntimeError("SpekConfig has not been initialized. Call SpekConfig.initialize() first.")
        return cls._root

    @classmethod
    def project_root(cls) -> Path:
        """Path to projects root directory"""
        if cls._root is None:
            raise RuntimeError("SpekConfig has not been initialized. Call SpekConfig.initialize() first.")
        return cls._root.parent

    @classmethod
    def reset(cls) -> None:
        cls._current = None
        cls._root = None

    @classmethod
    def load(cls, path: Path) -> SpekConfig:
        return load_yaml(path, cls)

    def save(self) -> None:
        save_yaml(self, self.root() / CONFIG_FILE)


@dataclass(eq=False)
class SourcedResource:
    source: str
    path: str

    @classmethod
    def parse(cls, ref: str) -> SourcedResource:
        """Split 'ns::bare/path' into ('ns', 'bare/path'). Defaults to ('spek', name)."""
        if SOURCED_RESOURCE_SOURCE_SEP in ref:
            ns, bare = ref.split(SOURCED_RESOURCE_SOURCE_SEP, 1)
        else:
            ns, bare = SPEK_SOURCE, ref
        return SourcedResource(source=ns, path=bare)

    @cached_property
    def as_string(self) -> str:
        if self.source != SPEK_SOURCE:
            return self.as_fully_qualified_string
        return self.path

    @cached_property
    def as_fully_qualified_string(self) -> str:
        return f"{self.source}{SOURCED_RESOURCE_SOURCE_SEP}{self.path}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourcedResource):
            return NotImplemented
        return self.as_fully_qualified_string == other.as_fully_qualified_string

    def __hash__(self) -> int:
        return hash(self.as_fully_qualified_string)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SourcedResource):
            return NotImplemented
        return self.as_fully_qualified_string < other.as_fully_qualified_string

    @classmethod
    def sanitize(cls, resources: Sequence[str] | str | set[str]) -> list[str]:
        if isinstance(resources, str):
            resources = [resources]
        sanitized: dict[str, str] = {}
        for r in resources:
            r = r.strip()
            r = SourcedResource.parse(r)
            sanitized[r.as_fully_qualified_string] = r.as_string
        sanitized_sorted = sorted(sanitized.items(), key=lambda f: f[0])
        return [i[1] for i in sanitized_sorted]
