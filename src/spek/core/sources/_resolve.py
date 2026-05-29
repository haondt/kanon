from __future__ import annotations

import functools
from typing import TypeVar, cast, override
from collections.abc import Iterable
import warnings

from spek.core.config import (
    ALIAS_SCHEME,
    GITHUB_SCHEME,
    GITLAB_SCHEME,
    LOCAL_SCHEME,
    PROJECT_ADDRESS,
    SELF_ADDRESS,
    SPEK_SCHEME,
    SPEK_ADDRESS,
    SourceReference,
    SourcedResource,
    SpekConfig,
)
from spek.core.settings import GlobalSettings
from spek.core.sources._base import ParsedSource, SourceResolver
from spek.core.sources._github import GitHubSource
from spek.core.sources._gitlab import GitLabSource
from spek.core.sources._local import LocalSource
from spek.core.sources._project import ProjectSource
from spek.core.sources._spek import SpekSource
from spek.core.sources._alias import AliasRef

T = TypeVar("T", SourceReference, SourcedResource)

class FullSourceResolver(SourceResolver):
    @override
    def dealias(self, ref: T) -> T:
        if isinstance(ref, SourceReference):
            if ref.scheme != ALIAS_SCHEME:
                return ref
            return self[ref].get_reference()
        if ref.source.scheme != ALIAS_SCHEME:
            return ref
        return SourcedResource(self[ref.source].get_reference(), ref.path)
    @override
    def resolve(self, ref: SourceReference) -> ParsedSource:
        result = self.try_resolve(ref)
        if result:
            return result
        raise KeyError(f"Could not resolve source {ref.as_string}")

    @override
    def try_resolve(self, ref: SourceReference) -> ParsedSource | None:
        sources = resolve_sources()
        if ref in sources:
            return sources[ref]
        if ref.scheme != SPEK_SCHEME and ref.scheme != ALIAS_SCHEME:
            return cast(ParsedSource, hydrate_source_reference(ref))
        return None

    @override
    def items(self) -> Iterable[tuple[SourceReference, ParsedSource]]:
        return resolve_sources().items()

    @override
    def __getitem__(self, ref: SourceReference) -> ParsedSource:
        return self.resolve(ref)

def initialize():
    SourceResolver.initialize(FullSourceResolver())

@functools.cache
def hydrate_source_reference(value: SourceReference) -> ParsedSource | AliasRef:
    """Parse a source value string into a ParsedSource or an AliasRef.

    Recognizes:
      - 'alias::name'         → AliasRef(name)
      - 'spek::spek'          → SpekSource (built-in)
      - 'spek::project'       → ProjectSource (built-in)
      - 'spek::self'          → SelfSource (built-in)
      - 'gh::org/repo[@ref]'  → GitHubSource
      - 'gl::g/.../r[@ref]'   → GitLabSource
      - 'local::path'         → LocalSource
      - bare path             → LocalSource (expanded)
    """
    if value.scheme == ALIAS_SCHEME:
        return AliasRef(value.address)
    if value.scheme == SPEK_SCHEME:
        if value.address == SPEK_ADDRESS:
            return _get_spek_source()
        if value.address == PROJECT_ADDRESS:
            return ProjectSource()
        if value.address == SELF_ADDRESS:
            raise ValueError("Cannot hydrate self source")
        raise ValueError(f"Unknown spek built-in source: {value!r}")
    if value.scheme == GITHUB_SCHEME:
        return GitHubSource.parse(value.address)
    if value.scheme == GITLAB_SCHEME:
        return GitLabSource.parse(value.address)
    if value.scheme == LOCAL_SCHEME:
        return LocalSource.parse(value.address)
    raise ValueError(f"Unrecognized source scheme {value.scheme!r} in value {value.as_fully_qualified_string!r}")

@functools.cache
def resolve_sources() -> dict[SourceReference, ParsedSource]:
    """Merge global + project sources (project wins).

    Returns a dict keyed by 'scheme::address'.

    Fixed merge order:
      1. spek::spek → SpekSource (default)
      2. global settings.yaml sources
      3. project spek.yaml sources (project wins on collision)
      4. spek::project → ProjectSource (non-shadowable, injected after merge)
      5. spek::self → SelfSource (non-shadowable, injected after merge)

    AliasRef values are resolved transitively after merge.
    Cycles raise ValueError.
    """
    merged: dict[SourceReference, ParsedSource | AliasRef] = {}

    spek_key = SourceReference.SPEK_SOURCE_REFERENCE
    merged[spek_key] = _get_spek_source()

    global_sources = { SourceReference.parse(k, validate_as_key=True): v for k, v in GlobalSettings.instance().sources.items() }
    project_config = SpekConfig.get()
    raw_project_sources = project_config.sources if project_config is not None else {}
    project_sources = { SourceReference.parse(k, validate_as_key=True): v for k, v in raw_project_sources.items()}

    for sources in (global_sources, project_sources):
        for source_key, source_value in sources.items():
            if source_key == spek_key:
                warnings.warn(
                    f"{spek_key.as_string} is shadowed by user-defined source: {source_value!r}",
                    stacklevel=2,
                )
            parsed = hydrate_source_reference(SourceReference.parse(source_value))
            merged[source_key] = parsed

    project_key = SourceReference.PROJECT_SOURCE_REFERENCE

    if project_config is not None:
        merged[project_key] = ProjectSource()

    merged_items = list(merged.items())
    resolved: dict[SourceReference, ParsedSource] = {}
    for source_key, source in merged_items:
        if isinstance(source, AliasRef):
            resolved_source = source.resolve(merged, [source_key])
            resolved[source_key] = resolved_source
            merged[source_key] = resolved_source
        else:
            resolved[source_key] = source
    return resolved


def _get_spek_source() -> ParsedSource:
    return SpekSource.create()
