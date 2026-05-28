from __future__ import annotations

import importlib.resources
import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from collections.abc import Sequence
from typing import Any, ClassVar, override
from pydantic import BaseModel

from spek.core.yaml_utils import load_yaml, save_yaml
from spek.core.utils import resolve_path

from functools import cached_property

REFERENCE_SEP = "::"
PROJECT_SPEK_DIR = ".spek"
CONFIG_FILE = "spek.yaml"

SYNCED_MODULES_DIR = "modules"
SYNCED_STANCES_DIR = "stances"

PROJECT_MODULES_DIR = "project/modules"
PROJECT_PROFILES_DIR = "project/profiles"
PROJECT_STANCES_DIR = "project/stances"
PROJECT_REFS_DIR = "project/references"

SPEK_ADDRESS = "spek"
PROJECT_ADDRESS = "project"
SELF_ADDRESS = "self"

ALIAS_SCHEME = "alias"
SPEK_SCHEME = "spek"
GITHUB_SCHEME = "gh"
GITLAB_SCHEME = "gl"
LOCAL_SCHEME = "local"
VALID_SCHEMES: frozenset[str] = frozenset({SPEK_SCHEME, ALIAS_SCHEME, GITHUB_SCHEME, GITLAB_SCHEME, LOCAL_SCHEME})
SPEK_BUILTIN_ADDRESSES: frozenset[str] = frozenset({SPEK_ADDRESS, PROJECT_ADDRESS, SELF_ADDRESS})

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
    frontmatter: dict[str, Any] = field(default_factory=dict)

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

@dataclass
class SourceReference:
    scheme: str
    address: str

    SPEK_SOURCE_REFERENCE: ClassVar[SourceReference]
    PROJECT_SOURCE_REFERENCE: ClassVar[SourceReference]
    SELF_SOURCE_REFERENCE: ClassVar[SourceReference]

    @classmethod
    def parse(cls, ref: str, *, sanitize: bool = False, validate_as_key: bool = False) -> SourceReference:
        """Parse a source reference string into scheme and address.

        Structural split only by default. Bare strings default to the alias scheme.

          - bare name (e.g. 'mywork')  → (alias, mywork)
          - 'scheme::address'          → (scheme, address)

        sanitize=True strips whitespace before parsing.
        validate_as_key=True enforces source config key constraints (raises ValueError).
        """
        if sanitize:
            ref = ref.strip()
        sep = REFERENCE_SEP
        if sep not in ref:
            if ref.startswith(("/", "~", "./")):
                result = SourceReference(LOCAL_SCHEME, ref)
            else:
                result = SourceReference(ALIAS_SCHEME, ref)
        else:
            prefix, rest = ref.split(sep, 1)
            if REFERENCE_SEP in rest:
                raise ValueError(f"Invalid source reference {ref!r}: must be in the format scheme{REFERENCE_SEP}address")
            result = SourceReference(prefix, rest)
        if validate_as_key:
            result.validate_as_key()
        return result

    def validate_as_key(self) -> None:
        """Validate that this SourceReference is valid as a source config dict key.

        Valid:  (alias, name) and (spek, spek)
        Invalid: gh/gl/local schemes; spek::project, spek::self, any other spek::*
        """
        if self.scheme == SPEK_SCHEME:
            if self.address != SPEK_ADDRESS:
                raise ValueError(
                    f"Invalid source key {self.as_fully_qualified_string!r}: " +
                    f"only '{SPEK_SCHEME}{REFERENCE_SEP}{SPEK_ADDRESS}' is allowed under the '{SPEK_SCHEME}' scheme; " +
                    f"'{SPEK_SCHEME}{REFERENCE_SEP}{PROJECT_ADDRESS}' and '{SPEK_SCHEME}{REFERENCE_SEP}{SELF_ADDRESS}' are reserved and non-shadowable"
                )
        elif self.scheme != ALIAS_SCHEME:
            raise ValueError(
                f"Invalid source key {self.as_fully_qualified_string!r}: " +
                f"prefixed keys must use '{ALIAS_SCHEME}{REFERENCE_SEP}' or '{SPEK_SCHEME}{REFERENCE_SEP}{SPEK_ADDRESS}'; " +
                f"got scheme {self.scheme!r}"
            )

    @cached_property
    def as_string(self) -> str:
        """Shortest unambiguous form."""
        if self.scheme == SPEK_SCHEME and self.address == SPEK_ADDRESS:
            return f'{self.scheme}{REFERENCE_SEP}{self.address}'
        if self.scheme == SPEK_SCHEME and self.address in SPEK_BUILTIN_ADDRESSES:
            return f"{self.address}"
        if self.scheme == ALIAS_SCHEME:
            return f"{self.address}"
        return self.as_fully_qualified_string

    @cached_property
    def as_fully_qualified_string(self) -> str:
        return f"{self.scheme}{REFERENCE_SEP}{self.address}"

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourceReference):
            return NotImplemented
        return self.as_fully_qualified_string == other.as_fully_qualified_string

    @override
    def __hash__(self) -> int:
        return hash(self.as_fully_qualified_string)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SourceReference):
            return NotImplemented
        return self.as_fully_qualified_string < other.as_fully_qualified_string

    @classmethod
    def sanitize(cls, references: Sequence[str] | str | set[str]) -> list[str]:
        if isinstance(references, str):
            references = [references]
        sanitized: dict[str, str] = {}
        for r in references:
            r = r.strip()
            r = SourceReference.parse(r)
            sanitized[r.as_fully_qualified_string] = r.as_string
        sanitized_sorted = sorted(sanitized.items(), key=lambda f: f[0])
        return [i[1] for i in sanitized_sorted]

SourceReference.SPEK_SOURCE_REFERENCE = SourceReference(SPEK_SCHEME, SPEK_ADDRESS)
SourceReference.PROJECT_SOURCE_REFERENCE = SourceReference(SPEK_SCHEME, PROJECT_ADDRESS)
SourceReference.SELF_SOURCE_REFERENCE = SourceReference(SPEK_SCHEME, SELF_ADDRESS)

@dataclass(eq=False)
class SourcedResource:
    source: SourceReference
    path: str

    @classmethod
    def parse(cls, ref: str) -> SourcedResource:
        """Parse a module reference string into (scheme, address, path).

        - 0 separators:         bare path  → (spek, spek, path)
        - 1 separator foo::bar:
            foo ∈ SPEK_BUILTIN_ADDRESSES → (spek, foo, bar)
            else                            → (alias, foo, bar)
        - 2 separators scheme::address::path → (scheme, address, path)
        - >2 separators → ValueError
        """
        sep_count = ref.count(REFERENCE_SEP)
        if sep_count > 2:
            raise ValueError(f"Invalid module reference: {ref!r} — too many '::' separators (max 2)")
        parts = ref.split(REFERENCE_SEP)
        if len(parts) == 1:
            return SourcedResource(SourceReference.SPEK_SOURCE_REFERENCE, path=ref)
        if len(parts) == 2:
            prefix, bare = parts
            if prefix in SPEK_BUILTIN_ADDRESSES:
                return SourcedResource(SourceReference(SPEK_SCHEME, prefix), path=bare)
            return SourcedResource(SourceReference(ALIAS_SCHEME, prefix), path=bare)
        scheme, address, path = parts
        return SourcedResource(SourceReference(scheme, address), path=path)

    @cached_property
    def as_string(self) -> str:
        """Shortest unambiguous form."""
        if self.source.scheme == SPEK_SCHEME and self.source.address == SPEK_ADDRESS:
            return self.path
        if self.source.scheme == SPEK_SCHEME and self.source.address in SPEK_BUILTIN_ADDRESSES:
            return f"{self.source.address}{REFERENCE_SEP}{self.path}"
        if self.source.scheme == ALIAS_SCHEME:
            return f"{self.source.address}{REFERENCE_SEP}{self.path}"
        return self.as_fully_qualified_string

    @cached_property
    def as_fully_qualified_string(self) -> str:
        return f"{self.source.as_fully_qualified_string}{REFERENCE_SEP}{self.path}"

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourcedResource):
            return NotImplemented
        return self.as_fully_qualified_string == other.as_fully_qualified_string

    @override
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

