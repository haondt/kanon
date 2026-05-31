from __future__ import annotations

from kanon.core.config import KanonEnv
from kanon.core.settings import GlobalSettings


def test_initialize_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(tmp_path / ".kanon" / "settings.yaml"))
    KanonEnv.reset()
    result = GlobalSettings.initialize()
    assert isinstance(result, GlobalSettings)
    assert result.sources == {}


def test_initialize_parses_sources(tmp_path, monkeypatch):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "settings.yaml").write_text("sources:\n  mywork: /some/path\n")
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(kanon_dir / "settings.yaml"))
    KanonEnv.reset()
    result = GlobalSettings.initialize()
    assert "mywork" in result.sources
    assert result.sources["mywork"] == "/some/path"


def test_initialize_multiple_sources(tmp_path, monkeypatch):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "settings.yaml").write_text(
        "sources:\n  corp: /corp/kanons\n  shared: ~/shared\n"
    )
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(kanon_dir / "settings.yaml"))
    KanonEnv.reset()
    result = GlobalSettings.initialize()
    assert "corp" in result.sources
    assert "shared" in result.sources
    assert result.sources["corp"] == "/corp/kanons"
    assert result.sources["shared"] == "~/shared"


def test_initialize_empty_file_returns_empty(tmp_path, monkeypatch):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "settings.yaml").write_text("{}\n")
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(kanon_dir / "settings.yaml"))
    KanonEnv.reset()
    result = GlobalSettings.initialize()
    assert result.sources == {}


def test_save_roundtrip(tmp_path, monkeypatch):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    monkeypatch.setenv("KANON_SETTINGS_PATH", str(kanon_dir / "settings.yaml"))
    KanonEnv.reset()
    settings = GlobalSettings.initialize()
    settings.sources["mywork"] = "/my/path"
    settings.save()
    reloaded = GlobalSettings.initialize()
    assert reloaded.sources["mywork"] == "/my/path"
