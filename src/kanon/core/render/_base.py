from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Callable
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, Self, override

import jinja2
from pydantic import BaseModel

from kanon.core.config import (
    KanonConfig,
    OutputType,
    SourcedResource,
)
from kanon.core.errors import KanonRuntimeError, KanonValueError
from kanon.core.kanons import Kanon

@dataclass
class DryCleanResult:
    files: list[Path] = field(default_factory=list)
    directories: list[Path] = field(default_factory=list)
    extra_info: str | None = None

    @classmethod
    def merge(cls, results: list[DryCleanResult]):
        files: set[Path] = set()
        directories: set[Path] = set()
        extra_infos: list[str] = []
        for r in results:
            files |= set(r.files)
            directories |= set(r.directories)
            if r.extra_info:
                extra_infos.append(r.extra_info)
        return DryCleanResult(
            files=list(files),
            directories=list(directories),
            extra_info='\n'.join(extra_infos) if extra_infos else None
        )

class SkillDirectoryConflictError(KanonRuntimeError):
    pass

class GlobalModeUnsupportedError(KanonValueError):
    @classmethod
    def render_error_message(cls, renderer_class: type | None | str = None):
        if renderer_class is None:
            renderer_class_name = "this renderer"
        elif isinstance(renderer_class, str):
            renderer_class_name = renderer_class
        else:
            renderer_class_name = renderer_class.__name__
        return f"Global mode is not supported for integration {renderer_class_name}"

    def __init__(self, renderer_class: type | None = None, message: str | None = None):
        if message is None:
            message = self.render_error_message(renderer_class)
        super().__init__(message)

class _ArgsDict(dict):  # pyright: ignore[reportMissingTypeArgument]
    """Returns False for missing keys so absent template args are falsy without raising."""

    def __missing__(self, key: str) -> bool:
        return False


def _apply_jinja(body: str, context: dict[str, Any]) -> str:
    env = jinja2.Environment(
        undefined=jinja2.StrictUndefined, keep_trailing_newline=True
    )
    return env.from_string(body).render(context)

@dataclass
class KanonRenderHelper:
    kanon: Kanon
    resource: SourcedResource

    @cached_property
    def meta(self):
        return self.kanon.frontmatter.kanon

    @cached_property
    def name(self):
        return self.meta.name or self.resource.as_string

    def validate(self) -> Self:
        if self.meta.output == OutputType.SKILL and not self.meta.name:
            raise ValueError(
                f"Skill kanon '{self.resource.as_string}' is missing kanon.name — skills require an explicit name"
            )
        return self

    def base_render_body(self):
        config = KanonConfig.instance()
        if self.meta.template == "jinja":
            return _apply_jinja(
                self.kanon.content,
                {
                    "kanons": config.kanons,
                    "integrations": config.meta.integrations,
                    "args": _ArgsDict(self.resource.args),
                    "source": self.resource.source.as_string,
                },
            )
        return self.kanon.content


@dataclass
class KanonRenderer(ABC):
    @classmethod
    def output_root(cls) -> Path:
        """Directory that this integration's output paths are relative to."""
        return KanonConfig.project_root()

    @classmethod
    @abstractmethod
    def render_rule(
        cls,
        resource: SourcedResource,
        frontmatter: dict[str, Any] | BaseModel | None,
        content: str,
    ) -> Path: ...

    @classmethod
    def render_bespoke_rules(cls,
        on_render_progress: Callable[[Path], None] | None = None,
    ):
        pass

    @classmethod
    @abstractmethod
    def render_settings(
        cls,
        preapproved_tools: list[str],
        on_progress: Callable[[str], None] | None = None,
    ) -> Path | None: ...

    @classmethod
    @abstractmethod
    def render_kanon(
        cls,
        kanon_resource: SourcedResource,
        kanon: Kanon,
        on_progress: Callable[[str], None] | None = None,
    ) -> Path: ...

    @classmethod
    @abstractmethod
    def dry_clean(cls) -> DryCleanResult: ...

    @classmethod
    def clean(cls, on_clean_progress: Callable[[str], None] | None = None):
        """Remove all kanon-managed files from a project."""
        root = cls.output_root()
        targets = cls.dry_clean()

        for t in targets.directories:
            if not t.exists():
                continue
            shutil.rmtree(t)
            if on_clean_progress:
                on_clean_progress(f"  removed {t.relative_to(root)}")
        for t in targets.files:
            if not t.exists():
                continue
            t.unlink()
            if on_clean_progress:
                on_clean_progress(f"  removed {t.relative_to(root)}")

class GlobalKanonRenderer(KanonRenderer, ABC):
    @classmethod
    @abstractmethod
    def global_root(cls) -> Path:
        """Directory this integration's output is written to in global mode."""
        ...

    @classmethod
    @override
    def output_root(cls) -> Path:
        """Directory that this integration's output paths are relative to."""
        return cls.global_root() if KanonConfig.is_global() else super().output_root()
