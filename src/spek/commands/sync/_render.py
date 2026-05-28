from __future__ import annotations

import shutil
from collections.abc import Sequence

import click

from spek.commands.sync._synced import read_synced_module
from spek.core.config import AI_TOOL_OUTPUT_DIRS, AI_TOOL_SETTINGS_FILES, AI_TOOL_SPECIFIC_RULES, OutputType, SourceReference, SourcedResource, SpekConfig
from spek.core.modules import Module
from spek.core.render import (
    render_module,
    render_settings,
)
from spek.core.render._module import render_rule


def render_all(to_render: Sequence[SourcedResource] | set[SourcedResource]) -> None:
    config = SpekConfig.instance()
    project_root = SpekConfig.project_root()

    for integration in config.meta.integrations:
        settings_rel = AI_TOOL_SETTINGS_FILES.get(integration)
        if settings_rel:
            (project_root / settings_rel).unlink(missing_ok=True)
        for rel_dir in set(AI_TOOL_OUTPUT_DIRS.get(integration, {}).values()):
            d = project_root / rel_dir
            if d.exists():
                shutil.rmtree(d)

    globally_preapproved_tools: set[str] = set()
    modules: dict[SourcedResource, Module] = {}
    for resource in to_render:
        module = read_synced_module(resource)
        modules[resource] = module
        if module.frontmatter.spek.output == OutputType.RULE:
            globally_preapproved_tools = globally_preapproved_tools | set(module.frontmatter.spek.preapproved_tools)

    for integration in config.meta.integrations:
        click.echo(f"Generating {integration} output:")
        for resource, module in modules.items():
            out_path = render_module(
                resource,
                module,
                integration
            )
            click.echo(f"  {resource.as_string} → {out_path.relative_to(project_root)}")

        rules = AI_TOOL_SPECIFIC_RULES.get(integration, [])
        for rule in rules:
            tool_rule_path = render_rule(
                SourcedResource(SourceReference.SPEK_SOURCE_REFERENCE, path=rule.path),
                rule.frontmatter,
                rule.content,
                integration
            )
            click.echo(f"  tool-specific-rules → {tool_rule_path.relative_to(project_root)}")
        render_settings(integration, globally_preapproved_tools)
