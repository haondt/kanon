from __future__ import annotations
from pathlib import Path

import pytest

from kanon.core.config import KanonConfig, KanonEnv
from kanon.core.settings import GlobalSettings
from kanon.core.sources import SourceResolver
from kanon.core.sources._resolve import resolve_sources, hydrate_source_reference, initialize


@pytest.fixture(autouse=True)
def reset_singletons(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(tmp_path / "settings.yaml"))
    KanonConfig.reset()
    GlobalSettings.reset()
    KanonEnv.reset()
    SourceResolver.reset()
    initialize()
    resolve_sources.cache_clear()
    hydrate_source_reference.cache_clear()
    yield
    resolve_sources.cache_clear()
    hydrate_source_reference.cache_clear()
