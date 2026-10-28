from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Protocol, override

from pydantic import BaseModel

from kanon.core.config import Integration, KanonConfig, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, GlobalKanonRenderer, GlobalModeUnsupportedError, KanonRenderer
from kanon.core.render._claude import ClaudeKanonRenderer
from kanon.core.render._codex import CodexKanonRenderer
from kanon.core.render._devin import DevinKanonRenderer
from kanon.core.render._opencode import OpenCodeKanonRenderer
from kanon.core.render._windsurf import WindsurfKanonRenderer

_RENDERERS: dict[Integration, type[KanonRenderer]] = {
    ClaudeKanonRenderer.INTEGRATION: ClaudeKanonRenderer,
    CodexKanonRenderer.INTEGRATION: CodexKanonRenderer,
    WindsurfKanonRenderer.INTEGRATION: WindsurfKanonRenderer,
    DevinKanonRenderer.INTEGRATION: DevinKanonRenderer,
    OpenCodeKanonRenderer.INTEGRATION: OpenCodeKanonRenderer,
}

class IntegrationRoots():
    def __init__(self, renderer_class: type[KanonRenderer]):
        self._renderer_class: type[KanonRenderer] = renderer_class

    @property
    def supports_global(self) -> bool:
        return False

    @property
    def global_root(self) -> Path:
        """Directory this integration's output is written to in global mode."""
        raise GlobalModeUnsupportedError(self._renderer_class)

    @property
    def try_global_root(self) -> Path | None:
        """Directory this integration's output is written to in global mode."""
        if self.supports_global:
            return self.global_root
        return None

    @property
    def output_root(self) -> Path:
        """Directory that this integration's output paths are relative to."""
        return self._renderer_class.output_root()

class GlobalIntegrationRoots(IntegrationRoots):
    def __init__(self, renderer_class: type[GlobalKanonRenderer]):
        self._global_renderer_class: type[GlobalKanonRenderer] = renderer_class
        super().__init__(renderer_class)

    @property
    @override
    def supports_global(self) -> bool:
        return True

    @property
    @override
    def global_root(self) -> Path:
        return self._global_renderer_class.global_root()

def roots(integration: Integration) -> IntegrationRoots:
    renderer = _renderer(integration)
    if issubclass(renderer, GlobalKanonRenderer):
        return GlobalIntegrationRoots(renderer)
    return IntegrationRoots(renderer)

def _renderer(integration: Integration) -> type[KanonRenderer]:
    return _RENDERERS[integration]

def render_rule(
    resource: SourcedResource,
    frontmatter: dict[str, Any] | BaseModel | None,
    content: str,
    integration: Integration,
) -> Path:
    return _renderer(integration).render_rule(resource, frontmatter, content)

def render_bespoke_rules(integration: Integration,
    on_render_progress: Callable[[Path], None] | None = None,
):
    return _renderer(integration).render_bespoke_rules(on_render_progress)


def render_kanon(
    kanon_resource: SourcedResource,
    kanon: Kanon,
    integration: Integration,
    on_progress: Callable[[str], None] | None = None,
) -> Path:
    return _renderer(integration).render_kanon(kanon_resource, kanon, on_progress)

def render_settings(
    integration: Integration,
    preapproved_tools: list[str] | set[str],
    on_progress: Callable[[str], None] | None = None,
) -> Path | None:
    preapproved_tools = sorted(preapproved_tools) if isinstance(preapproved_tools, set) else preapproved_tools
    return _renderer(integration).render_settings(preapproved_tools, on_progress)

def dry_clean_all(integration: Integration) -> DryCleanResult:
    return _renderer(integration).dry_clean()


def clean_all(integration: Integration,
    on_clean_progress: Callable[[str], None] | None = None,
):
    return _renderer(integration).clean(on_clean_progress)
