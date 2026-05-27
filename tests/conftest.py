from __future__ import annotations

import pytest

from spek.core.config import SpekConfig, SpekEnv
from spek.core.settings import GlobalSettings
from spek.core.sources._resolve import resolve_sources, parse_source_ref


@pytest.fixture(autouse=True)
def reset_singletons(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(tmp_path / "settings.yaml"))
    SpekConfig.reset()
    GlobalSettings.reset()
    SpekEnv.reset()
    resolve_sources.cache_clear()
    parse_source_ref.cache_clear()
    yield
    resolve_sources.cache_clear()
    parse_source_ref.cache_clear()
