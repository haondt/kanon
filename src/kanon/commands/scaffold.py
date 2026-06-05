from __future__ import annotations

import click
import questionary
from questionary import Choice

from kanon import __version__
from kanon.core.config import SourceReference, KanonConfig, KanonMeta, SourcedResource
from kanon.core.config import AI_TOOL_OUTPUT_DIRS
from kanon.core.sources import SourceResolver

INTEGRATIONS = list(AI_TOOL_OUTPUT_DIRS)


@click.command()
def init() -> None:
    """Interactively initialize a new project with kanon conventions."""
    if KanonConfig.get() is not None:
        click.echo(".kanon/kanon.yaml already exists. Run 'kanon sync' to update.")
        raise SystemExit(1)

    KanonConfig.root().mkdir(parents=True, exist_ok=True)

    sources = SourceResolver.instance()

    integrations = questionary.checkbox(
        "Select integrations:",
        choices=INTEGRATIONS,
        use_jk_keys=False,
    ).ask()
    if integrations is None:
        click.echo("No integrations selected. Aborting.")
        raise SystemExit(1)

    selected_kanons: list[str] | None = []
    selected_stances: list[str] | None = []
    chosen_profile: str | None = None

    profile_refs = sorted(
        [SourcedResource(source_key, path) for source_key, source in sources.items() for path in source.list_profiles()],
        key=lambda r: r.as_fully_qualified_string,
    )
    profiles = {r.as_string: sources[r.source].shallow_hydrate_profile(r.path) for r in profile_refs}

    if profiles:
        profile_choice = questionary.select(
            "Start from a profile?",
            choices=["none"] + list(profiles.keys()),
            use_jk_keys=False,
        ).ask()
        if profile_choice is None:
            raise SystemExit(1)
        if profile_choice != "none":
            chosen_profile = profile_choice
            ref = SourcedResource.parse(profile_choice)
            resolved = sources[ref.source].hydrate_profile(ref)
            selected_kanons = resolved.kanons
            selected_stances = resolved.stances
            click.echo(f"Loaded {len(selected_kanons)} kanons and {len(selected_stances)} stances from '{profile_choice}'.")

    available_kanons = sorted(
        [SourcedResource(source_key, path) for source_key, source in sources.items() for path in source.list_kanons()],
        key=lambda r: r.as_fully_qualified_string,
    )
    kanon_names = [r.as_string for r in available_kanons]
    selected_set = set(selected_kanons)
    kanon_choices = [Choice(name, checked=(name in selected_set)) for name in kanon_names]
    selected_kanons = questionary.checkbox(
        "Select kanons:",
        choices=kanon_choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if selected_kanons is None:
        click.echo("No kanons selected. Aborting.")
        raise SystemExit(1)

    sha = sources[SourceReference.KANON_SOURCE_REFERENCE].get_sha()
    config = KanonConfig(
        meta=KanonMeta(kanon_version=__version__, kanon_sha=sha, integrations=integrations, profile=chosen_profile),
        kanons=selected_kanons,
        stances=selected_stances,
    )
    config.save()
    click.echo(f"\nWrote .kanon/kanon.yaml with {len(selected_kanons)} kanon(s) pinned at {sha[:8]}.")
    click.echo("Run 'kanon sync' to copy kanon files and emit AI tool rules.")
