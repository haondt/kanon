from __future__ import annotations

import shutil
from collections.abc import Sequence

import click

from kanon.commands.sync._synced import read_synced_kanon
from kanon.core.config import AI_TOOL_OUTPUT_DIRS, AI_TOOL_SETTINGS_FILES, AI_TOOL_SPECIFIC_RULES, OutputType, SourceReference, SourcedResource, KanonConfig
from kanon.core.kanons import Kanon
from kanon.core.render import (
    render_kanon,
    render_settings,
)
from kanon.core.render._kanon import render_rule


def render_all(to_render: Sequence[SourcedResource] | set[SourcedResource]) -> None:
    config = KanonConfig.instance()
    project_root = KanonConfig.project_root()

    for integration in config.meta.integrations:
        settings_rel = AI_TOOL_SETTINGS_FILES.get(integration)
        if settings_rel:
            (project_root / settings_rel).unlink(missing_ok=True)
        for rel_dir in set(AI_TOOL_OUTPUT_DIRS.get(integration, {}).values()):
            d = project_root / rel_dir
            if d.exists():
                shutil.rmtree(d)

    globally_preapproved_tools: set[str] = set()
    kanons: dict[SourcedResource, Kanon] = {}
    for resource in to_render:
        kanon = read_synced_kanon(resource)
        kanons[resource] = kanon
        if kanon.frontmatter.kanon.output == OutputType.RULE:
            globally_preapproved_tools = globally_preapproved_tools | set(kanon.frontmatter.kanon.preapproved_tools)

    for integration in config.meta.integrations:
        click.echo(f"Generating {integration} output:")
        for resource, kanon in kanons.items():
            out_path = render_kanon(
                resource,
                kanon,
                integration
            )
            click.echo(f"  {resource.as_string} → {out_path.relative_to(project_root)}")

        rules = AI_TOOL_SPECIFIC_RULES.get(integration, [])
        for rule in rules:
            tool_rule_path = render_rule(
                SourcedResource(SourceReference.KANON_SOURCE_REFERENCE, path=rule.path),
                rule.frontmatter,
                rule.content,
                integration
            )
            click.echo(f"  tool-specific-rules → {tool_rule_path.relative_to(project_root)}")
        render_settings(integration, globally_preapproved_tools)
