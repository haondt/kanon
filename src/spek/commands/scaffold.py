from __future__ import annotations

import click
import questionary
from questionary import Choice

from spek import __version__
from spek.core.config import SourceReference, SpekConfig, SpekMeta, SourcedResource
from spek.core.config import AI_TOOL_OUTPUT_DIRS
from spek.core.sources import SourceResolver

INTEGRATIONS = list(AI_TOOL_OUTPUT_DIRS)


@click.command()
def init() -> None:
    """Interactively initialize a new project with spek conventions."""
    if SpekConfig.get() is not None:
        click.echo(".spek/spek.yaml already exists. Run 'spek sync' to update.")
        raise SystemExit(1)

    SpekConfig.root().mkdir(parents=True, exist_ok=True)

    sources = SourceResolver.instance()

    integrations = questionary.checkbox(
        "Select integrations:",
        choices=INTEGRATIONS,
        use_jk_keys=False,
    ).ask()
    if integrations is None:
        click.echo("No integrations selected. Aborting.")
        raise SystemExit(1)

    selected_modules: list[str] | None = []
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
            resolved = sources[ref.source].hydrate_profile(ref.path)
            selected_modules = resolved.modules
            selected_stances = resolved.stances
            click.echo(f"Loaded {len(selected_modules)} modules and {len(selected_stances)} stances from '{profile_choice}'.")

    available_modules = sorted(
        [SourcedResource(source_key, path) for source_key, source in sources.items() for path in source.list_modules()],
        key=lambda r: r.as_fully_qualified_string,
    )
    module_names = [r.as_string for r in available_modules]
    selected_set = set(selected_modules)
    module_choices = [Choice(name, checked=(name in selected_set)) for name in module_names]
    selected_modules = questionary.checkbox(
        "Select modules:",
        choices=module_choices,
        use_search_filter=True,
        use_jk_keys=False,
    ).ask()

    if selected_modules is None:
        click.echo("No modules selected. Aborting.")
        raise SystemExit(1)

    sha = sources[SourceReference.SPEK_SOURCE_REFERENCE].get_sha()
    config = SpekConfig(
        meta=SpekMeta(spek_version=__version__, spek_sha=sha, integrations=integrations, profile=chosen_profile),
        modules=selected_modules,
        stances=selected_stances,
    )
    config.save()
    click.echo(f"\nWrote .spek/spek.yaml with {len(selected_modules)} module(s) pinned at {sha[:8]}.")
    click.echo("Run 'spek sync' to copy spec files and emit AI tool rules.")
