from __future__ import annotations

import functools
from pathlib import Path

from spek.core.config import PROJECT_SOURCE, SPEK_SOURCE, SpekEnv, SourcedResource, SpekConfig
from spek.core.settings import GlobalSettings
from spek.core.sources._base import ParsedSource
from spek.core.sources._github import GITHUB_SOURCE_TYPE_ID, GitHubSource
from spek.core.sources._gitlab import GITLAB_SOURCE_TYPE_ID, GitLabSource
from spek.core.sources._local import LOCAL_SOURCE_TYPE_ID, LocalSource
from spek.core.sources._project import ProjectSource
from spek.core.sources._base import SourceResolver
from spek.core.sources._spek import SpekSource


_resolver = SourceResolver(
    get=lambda k: resolve_sources()[k],
    try_get=lambda k: resolve_sources().get(k)
)

def _parse_source(path: str | Path | ParsedSource) -> ParsedSource:
    if isinstance(path, str):
        path = parse_source_ref(path)
    elif isinstance(path, Path):
        path = LocalSource(_resolver=_resolver, root=path.expanduser().resolve())
    return path

@functools.cache
def parse_source_ref(path: str) -> ParsedSource:
    """Classify a source path string.

    - Local: anything not starting with gh:: or gl::
      Expands ~ and resolves to absolute.
    - gh::org/repo[@ref] — GitHub
    - gl::group/.../repo[@ref] — GitLab (two or more path segments before optional @ref)
    """
    resource = SourcedResource.parse(path)
    if resource.source == GITHUB_SOURCE_TYPE_ID:
        return GitHubSource.parse(_resolver, resource.path)
    if resource.source == GITLAB_SOURCE_TYPE_ID:
        return GitLabSource.parse(_resolver, resource.path)
    if resource.source == LOCAL_SOURCE_TYPE_ID:
        return LocalSource.parse(_resolver, resource.path)
    return LocalSource.parse(_resolver, path)

@functools.cache
def resolve_sources() -> dict[str, ParsedSource]:
    """Merge global + project sources (project wins).

    'spek' namespace may be overridden by either sources dict; if not provided,
    it defaults to repo_path / 'specs' when repo_path is not None.
    """
    merged: dict[str, ParsedSource] = { SPEK_SOURCE: _get_spek_source() }
    project_config = SpekConfig.get()
    if project_config is not None:
        merged[PROJECT_SOURCE] = ProjectSource(_resolver=_resolver)
    global_sources = GlobalSettings.instance().sources
    if project_config is not None:
        project_sources = project_config.sources
    else:
        project_sources = {}
    for sources in (global_sources, project_sources):
        for ns, spec in sources.items():
            merged[ns] = _parse_source(spec)
    return merged

def _get_spek_source() -> ParsedSource:
    # TODO: temporary measure until we move the core spek specs to their own repo
    return SpekSource(_resolver=_resolver, root=SpekEnv.instance().repo_path)
