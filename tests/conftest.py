from __future__ import annotations
from pathlib import Path

import pytest

from spek.core.config import SpekConfig, SpekEnv
from spek.core.settings import GlobalSettings
from spek.core.sources import SourceResolver
from spek.core.sources._resolve import resolve_sources, hydrate_source_reference, initialize


@pytest.fixture(autouse=True)
def reset_singletons(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(tmp_path / "settings.yaml"))
    SpekConfig.reset()
    GlobalSettings.reset()
    SpekEnv.reset()
    SourceResolver.reset()
    initialize()
    resolve_sources.cache_clear()
    hydrate_source_reference.cache_clear()
    yield
    resolve_sources.cache_clear()
    hydrate_source_reference.cache_clear()
