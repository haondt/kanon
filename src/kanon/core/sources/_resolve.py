from __future__ import annotations

import functools
from typing import TypeVar, cast, override
from collections.abc import Iterable
import warnings

from kanon.core.config import (
    ALIAS_SCHEME,
    GITHUB_SCHEME,
    GITLAB_SCHEME,
    LOCAL_SCHEME,
    PROJECT_ADDRESS,
    SELF_ADDRESS,
    KANON_SCHEME,
    KANON_ADDRESS,
    SourceReference,
    SourcedResource,
    KanonConfig,
)
from kanon.core.settings import GlobalSettings
from kanon.core.sources._base import ParsedSource, SourceResolver
from kanon.core.sources._github import GitHubSource
from kanon.core.sources._gitlab import GitLabSource
from kanon.core.sources._local import LocalSource
from kanon.core.sources._project import ProjectSource
from kanon.core.sources._kanon_source import KanonSource
from kanon.core.sources._alias import AliasRef

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
        if ref.scheme != KANON_SCHEME and ref.scheme != ALIAS_SCHEME:
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
      - 'kanon::kanon'         → KanonSource (built-in)
      - 'kanon::project'      → ProjectSource (built-in)
      - 'kanon::self'         → SelfSource (built-in)
      - 'gh::org/repo[@ref]'  → GitHubSource
      - 'gl::g/.../r[@ref]'   → GitLabSource
      - 'local::path'         → LocalSource
      - bare path             → LocalSource (expanded)
    """
    if value.scheme == ALIAS_SCHEME:
        return AliasRef(value.address)
    if value.scheme == KANON_SCHEME:
        if value.address == KANON_ADDRESS:
            return _get_kanon_source()
        if value.address == PROJECT_ADDRESS:
            return ProjectSource()
        if value.address == SELF_ADDRESS:
            raise ValueError("Cannot hydrate self source")
        raise ValueError(f"Unknown kanon built-in source: {value!r}")
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
      1. kanon::kanon → KanonSource (default)
      2. global settings.yaml sources
      3. project kanon.yaml sources (project wins on collision)
      4. kanon::project → ProjectSource (non-shadowable, injected after merge)
      5. kanon::self → SelfSource (non-shadowable, injected after merge)

    AliasRef values are resolved transitively after merge.
    Cycles raise ValueError.
    """
    merged: dict[SourceReference, ParsedSource | AliasRef] = {}

    kanon_key = SourceReference.KANON_SOURCE_REFERENCE
    merged[kanon_key] = _get_kanon_source()

    global_sources = { SourceReference.parse(k, validate_as_key=True): v for k, v in GlobalSettings.instance().sources.items() }
    project_config = KanonConfig.get()
    raw_project_sources = project_config.sources if project_config is not None else {}
    project_sources = { SourceReference.parse(k, validate_as_key=True): v for k, v in raw_project_sources.items()}

    for sources in (global_sources, project_sources):
        for source_key, source_value in sources.items():
            if source_key == kanon_key:
                warnings.warn(
                    f"{kanon_key.as_string} is shadowed by user-defined source: {source_value!r}",
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


def _get_kanon_source() -> ParsedSource:
    return KanonSource.create()
