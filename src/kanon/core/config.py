from __future__ import annotations

import importlib.resources
import os
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from collections.abc import Sequence
from typing import Any, ClassVar, override
import urllib.parse
from pydantic import BaseModel

from kanon.core.yaml_utils import load_yaml, save_yaml
from kanon.core.utils import resolve_path

from functools import cached_property

REFERENCE_SEP = "::"
PROJECT_KANON_DIR = ".kanon"
CONFIG_FILE = "kanon.yaml"

SYNCED_KANONS_DIR = "kanons"
SYNCED_STANCES_DIR = "stances"

PROJECT_KANONS_DIR = "project/kanons"
PROJECT_PROFILES_DIR = "project/profiles"
PROJECT_STANCES_DIR = "project/stances"
PROJECT_REFS_DIR = "project/references"

KANON_ADDRESS = "kanon"
PROJECT_ADDRESS = "project"
SELF_ADDRESS = "self"

ALIAS_SCHEME = "alias"
KANON_SCHEME = "kanon"
GITHUB_SCHEME = "gh"
GITLAB_SCHEME = "gl"
LOCAL_SCHEME = "local"
VALID_SCHEMES: frozenset[str] = frozenset({KANON_SCHEME, ALIAS_SCHEME, GITHUB_SCHEME, GITLAB_SCHEME, LOCAL_SCHEME})
KANON_BUILTIN_ADDRESSES: frozenset[str] = frozenset({KANON_ADDRESS, PROJECT_ADDRESS, SELF_ADDRESS})

SOURCED_KANONS_DIR = "kanons"
SOURCED_REFS_DIR = "references"
SOURCED_PROFILES_DIR = "profiles"
SOURCED_STANCES_DIR = "stances"

class OutputType(StrEnum):
    RULE = "rule"
    SKILL = "skill"


class Integration(StrEnum):
    CLAUDE = "claude"
    WINDSURF = "windsurf"
    DEVIN = "devin"

@dataclass
class IntegrationSpecificRule:
    path: str
    content: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    args: dict[str, str | bool] = field(default_factory=dict)

AI_TOOL_OUTPUT_DIRS: dict[Integration, dict[OutputType, str]] = {
    Integration.CLAUDE: {
        OutputType.RULE: ".claude/rules",
        OutputType.SKILL: ".claude/skills",
    },
    Integration.WINDSURF: {
        OutputType.RULE: ".windsurf/rules",
        OutputType.SKILL: ".windsurf/workflows",
    },
    Integration.DEVIN: {
        OutputType.RULE: ".devin/rules",
        OutputType.SKILL: ".devin/workflows",
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
- CRITICAL: The first action in every conversation is reading @.kanon/STRUCTURE.md. Do not respond to the user, write any files or plan any actions until this is complete.
- When running shell commands, prefer using the bash tool over interactive shell execution for better syntax highlighting in the chat window.
- Run `kanon` commands via blocking `run_command` calls; never background + `command_status`.""",
        )
    ],
    Integration.DEVIN: [
        IntegrationSpecificRule(
            path="devin-rules",
            frontmatter={"trigger": "always_on"},
            content="""## Project structure
- CRITICAL: The first action in every conversation is reading @.kanon/STRUCTURE.md. Do not respond to the user, write any files or plan any actions until this is complete.
- When running shell commands, prefer using the bash tool over interactive shell execution for better syntax highlighting in the chat window.
- Run `kanon` commands via blocking `run_command` calls; never background + `command_status`.""",
        )
    ],
}

class KanonEnv:
    """Environment-sourced configuration singleton. Values are lazily cached per instance."""
    _instance: ClassVar[KanonEnv | None] = None

    @classmethod
    def instance(cls) -> KanonEnv:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @cached_property
    def repo_path(self) -> Path:
        if val := os.environ.get("KANON_REPO_PATH"):
            return Path(val)
        pkg_path = Path(importlib.resources.files("kanon").__str__())
        candidate = pkg_path
        while candidate != candidate.parent:
            if (candidate / ".git").exists():
                return candidate
            candidate = candidate.parent
        raise RuntimeError("Could not locate kanon repo root (no .git found)")

    @cached_property
    def settings_path(self) -> Path:
        if val := os.environ.get("KANON_SETTINGS_PATH"):
            return Path(val)
        return Path.home() / ".kanon" / "settings.yaml"

    @cached_property
    def sources_cache_path(self) -> Path:
        if val := os.environ.get("KANON_SOURCES_CACHE_PATH"):
            return Path(val)
        return Path.home() / ".kanon" / "sources"



class KanonMeta(BaseModel):
    kanon_version: str
    kanon_sha: str
    integrations: list[Integration]
    profile: str | None = None


class KanonConfig(BaseModel):
    _current: ClassVar[KanonConfig | None] = None
    _root: ClassVar[Path | None] = None

    meta: KanonMeta
    kanons: list[str] = []
    stances: list[str] = []
    sources: dict[str, str] = {}

    @property
    def stances_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.stances]

    @property
    def kanons_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.kanons]

    @classmethod
    def initialize(cls, project_root: Path | str | None = None) -> None:
        root = resolve_path(project_root) / PROJECT_KANON_DIR
        cls._root = root
        cls._current = None
        config_path = root / CONFIG_FILE
        if not config_path.exists():
            return None
        cls._current = load_yaml(config_path, cls)

    @classmethod
    def instance(cls) -> KanonConfig:
        if cls._current is None:
            raise RuntimeError("No kanon.yaml found in the current directory.")
        return cls._current

    @classmethod
    def get(cls) -> KanonConfig | None:
        return cls._current

    @classmethod
    def root(cls) -> Path:
        """Path to projects .kanon directory"""
        if cls._root is None:
            raise RuntimeError("KanonConfig has not been initialized. Call KanonConfig.initialize() first.")
        return cls._root

    @classmethod
    def project_root(cls) -> Path:
        """Path to projects root directory"""
        if cls._root is None:
            raise RuntimeError("KanonConfig has not been initialized. Call KanonConfig.initialize() first.")
        return cls._root.parent

    @classmethod
    def reset(cls) -> None:
        cls._current = None
        cls._root = None

    @classmethod
    def load(cls, path: Path) -> KanonConfig:
        return load_yaml(path, cls)

    def save(self) -> None:
        save_yaml(self, self.root() / CONFIG_FILE)


_cache_path_safe: str = '-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

@dataclass
class SourceReference:
    scheme: str
    address: str

    KANON_SOURCE_REFERENCE: ClassVar[SourceReference]
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

        Valid:  (alias, name) and (kanon, kanon)
        Invalid: gh/gl/local schemes; kanon::project, kanon::self, any other kanon::*
        """
        if self.scheme == KANON_SCHEME:
            if self.address != KANON_ADDRESS:
                raise ValueError(
                    f"Invalid source key {self.as_fully_qualified_string!r}: " +
                    f"only '{KANON_SCHEME}{REFERENCE_SEP}{KANON_ADDRESS}' is allowed under the '{KANON_SCHEME}' scheme; " +
                    f"'{KANON_SCHEME}{REFERENCE_SEP}{PROJECT_ADDRESS}' and '{KANON_SCHEME}{REFERENCE_SEP}{SELF_ADDRESS}' are reserved and non-shadowable"
                )
        elif self.scheme != ALIAS_SCHEME:
            raise ValueError(
                f"Invalid source key {self.as_fully_qualified_string!r}: " +
                f"prefixed keys must use '{ALIAS_SCHEME}{REFERENCE_SEP}' or '{KANON_SCHEME}{REFERENCE_SEP}{KANON_ADDRESS}'; " +
                f"got scheme {self.scheme!r}"
            )

    @cached_property
    def as_string(self) -> str:
        """Shortest unambiguous form."""
        if self.scheme == KANON_SCHEME and self.address == KANON_ADDRESS:
            return f'{self.scheme}{REFERENCE_SEP}{self.address}'
        if self.scheme == KANON_SCHEME and self.address in KANON_BUILTIN_ADDRESSES:
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

    def cache_subpath(self) -> str:
        return f'{urllib.parse.quote(self.scheme, _cache_path_safe)}/{urllib.parse.quote(self.address, _cache_path_safe)}'

    @classmethod
    def from_cache_subpath(cls, scheme_part: str, address_part: str) -> SourceReference:
        return cls(
            scheme=urllib.parse.unquote(scheme_part),
            address=urllib.parse.unquote(address_part),
        )

    def cache_path(self) -> Path:
        return KanonEnv.instance().sources_cache_path / self.cache_subpath()

SourceReference.KANON_SOURCE_REFERENCE = SourceReference(KANON_SCHEME, KANON_ADDRESS)
SourceReference.PROJECT_SOURCE_REFERENCE = SourceReference(KANON_SCHEME, PROJECT_ADDRESS)
SourceReference.SELF_SOURCE_REFERENCE = SourceReference(KANON_SCHEME, SELF_ADDRESS)

_ARGS_RE = re.compile(r'\[([^\]]*)\]$')


@dataclass(eq=False)
class SourcedResource:
    source: SourceReference
    path: str
    args: dict[str, str | bool] = field(default_factory=dict)

    @classmethod
    def parse(cls, ref: str) -> SourcedResource:
        """Parse a kanon reference string into (scheme, address, path).

        - 0 separators:         bare path  → (kanon, kanon, path)
        - 1 separator foo::bar:
            foo ∈ KANON_BUILTIN_ADDRESSES → (kanon, foo, bar)
            else                            → (alias, foo, bar)
        - 2 separators scheme::address::path → (scheme, address, path)
        - >2 separators → ValueError

        An optional [...] suffix on the path encodes rendering args:
            foo/bar[flag]       → args={"flag": True}
            foo/bar[key=val]    → args={"key": "val"}
        """
        args: dict[str, str | bool] = {}
        if m := _ARGS_RE.search(ref):
            for part in m.group(1).split(','):
                part = part.strip()
                if not part:
                    continue
                if '=' in part:
                    k, v = part.split('=', 1)
                    args[k.strip()] = v.strip()
                else:
                    args[part] = True
            ref = ref[:m.start()]

        sep_count = ref.count(REFERENCE_SEP)
        if sep_count > 2:
            raise ValueError(f"Invalid kanon reference: {ref!r} — too many '::' separators (max 2)")
        parts = ref.split(REFERENCE_SEP)
        if len(parts) == 1:
            return SourcedResource(SourceReference.KANON_SOURCE_REFERENCE, path=ref, args=args)
        if len(parts) == 2:
            prefix, bare = parts
            if prefix in KANON_BUILTIN_ADDRESSES:
                return SourcedResource(SourceReference(KANON_SCHEME, prefix), path=bare, args=args)
            return SourcedResource(SourceReference(ALIAS_SCHEME, prefix), path=bare, args=args)
        scheme, address, path = parts
        return SourcedResource(SourceReference(scheme, address), path=path, args=args)

    def _format_args(self) -> str:
        if not self.args:
            return ""
        parts: list[str] = []
        for k in sorted(self.args):
            v = self.args[k]
            parts.append(k if v is True else f"{k}={v}")
        return f"[{','.join(parts)}]"

    @cached_property
    def as_string(self) -> str:
        """Shortest unambiguous form, including any args suffix."""
        args_suffix = self._format_args()
        if self.source.scheme == KANON_SCHEME and self.source.address == KANON_ADDRESS:
            return self.path + args_suffix
        if self.source.scheme == KANON_SCHEME and self.source.address in KANON_BUILTIN_ADDRESSES:
            return f"{self.source.address}{REFERENCE_SEP}{self.path}" + args_suffix
        if self.source.scheme == ALIAS_SCHEME:
            return f"{self.source.address}{REFERENCE_SEP}{self.path}" + args_suffix
        return self.as_fully_qualified_string

    @cached_property
    def as_path_string(self) -> str:
        """Source + path without args — used for file paths and sync identity."""
        return f"{self.source.as_fully_qualified_string}{REFERENCE_SEP}{self.path}"

    @cached_property
    def as_fully_qualified_string(self) -> str:
        """Complete canonical form including args."""
        return self.as_path_string + self._format_args()

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
            sanitized[r.as_path_string] = r.as_string
        sanitized_sorted = sorted(sanitized.items(), key=lambda f: f[0])
        return [i[1] for i in sanitized_sorted]
