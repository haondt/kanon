from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from kanon.core.config import Integration, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.render._base import DryCleanResult, KanonRenderer
from kanon.core.render._claude import ClaudeKanonRenderer
from kanon.core.render._codex import CodexKanonRenderer
from kanon.core.render._devin import DevinKanonRenderer
from kanon.core.render._opencode import OpenCodeKanonRenderer
from kanon.core.render._windsurf import WindsurfKanonRenderer

_RENDERERS: dict[Integration, type[KanonRenderer]] = {
    Integration.CLAUDE: ClaudeKanonRenderer,
    Integration.CODEX: CodexKanonRenderer,
    Integration.WINDSURF: WindsurfKanonRenderer,
    Integration.DEVIN: DevinKanonRenderer,
    Integration.OPENCODE: OpenCodeKanonRenderer,
}


def render_rule(
    resource: SourcedResource,
    frontmatter: dict[str, Any] | BaseModel | None,
    content: str,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].render_rule(resource, frontmatter, content)

def render_bespoke_rules(integration: Integration,
    on_render_progress: Callable[[Path], None] | None = None
):
    return _RENDERERS[integration].render_bespoke_rules(on_render_progress)


def render_kanon(
    kanon_resource: SourcedResource,
    kanon: Kanon,
    integration: Integration,
) -> Path:
    return _RENDERERS[integration].render_kanon(kanon_resource, kanon)

def render_settings(
    integration: Integration,
    preapproved_tools: list[str] | set[str],
) -> Path | None:
    preapproved_tools = sorted(preapproved_tools) if isinstance(preapproved_tools, set) else preapproved_tools
    return _RENDERERS[integration].render_settings(preapproved_tools)

def dry_clean_all(integration: Integration) -> DryCleanResult:
    return _RENDERERS[integration].dry_clean()


def clean_all(integration: Integration,
    on_clean_progress: Callable[[str], None] | None = None
):
    return _RENDERERS[integration].clean(on_clean_progress)
