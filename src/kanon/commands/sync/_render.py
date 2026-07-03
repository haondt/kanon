from __future__ import annotations

from collections.abc import Sequence

import click

from kanon.commands.sync._synced import read_synced_kanon
from kanon.core.config import (
    KanonConfig,
    OutputType,
    SourcedResource,
)
from kanon.core.kanons import Kanon
from kanon.core.render import (
    render_kanon,
    render_settings,
    clean_all,
    render_bespoke_rules
)


def render_all(to_render: Sequence[SourcedResource] | set[SourcedResource]) -> None:
    config = KanonConfig.instance()
    project_root = KanonConfig.project_root()

    for integration in config.meta.integrations:
        clean_all(integration)

    globally_preapproved_tools: set[str] = set()
    kanons: dict[SourcedResource, Kanon] = {}
    for resource in sorted(to_render, key=lambda r: r.as_fully_qualified_string):
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

        render_bespoke_rules(integration, lambda tool_rule_path: click.echo(f"  bespoke-rules → {tool_rule_path.relative_to(project_root)}"))
        render_settings(integration, globally_preapproved_tools)
