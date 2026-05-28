from spek.core.sources._base import ParsedSource
from spek.core.sources._filesystem import FilesystemSource
from spek.core.sources._local import LocalSource
from spek.core.sources._github import GitHubSource
from spek.core.sources._gitlab import GitLabSource
from spek.core.sources._project import ProjectSource
from spek.core.sources._self import SelfSource
from spek.core.sources._alias import AliasRef
from spek.core.sources._resolve import hydrate_source_reference, resolve_sources

__all__ = [
    "ParsedSource",
    "FilesystemSource",
    "LocalSource",
    "GitHubSource",
    "GitLabSource",
    "ProjectSource",
    "SelfSource",
    "AliasRef",
    "hydrate_source_reference",
    "resolve_sources",
]
