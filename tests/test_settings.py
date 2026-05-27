from __future__ import annotations

from spek.core.config import SpekEnv
from spek.core.settings import GlobalSettings


def test_initialize_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(tmp_path / ".spek" / "settings.yaml"))
    SpekEnv.reset()
    result = GlobalSettings.initialize()
    assert isinstance(result, GlobalSettings)
    assert result.sources == {}


def test_initialize_parses_sources(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "settings.yaml").write_text("sources:\n  mywork: /some/path\n")
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(spek_dir / "settings.yaml"))
    SpekEnv.reset()
    result = GlobalSettings.initialize()
    assert "mywork" in result.sources
    assert result.sources["mywork"] == "/some/path"


def test_initialize_multiple_sources(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "settings.yaml").write_text(
        "sources:\n  corp: /corp/specs\n  shared: ~/shared\n"
    )
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(spek_dir / "settings.yaml"))
    SpekEnv.reset()
    result = GlobalSettings.initialize()
    assert "corp" in result.sources
    assert "shared" in result.sources
    assert result.sources["corp"] == "/corp/specs"
    assert result.sources["shared"] == "~/shared"


def test_initialize_empty_file_returns_empty(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "settings.yaml").write_text("{}\n")
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(spek_dir / "settings.yaml"))
    SpekEnv.reset()
    result = GlobalSettings.initialize()
    assert result.sources == {}


def test_save_roundtrip(tmp_path, monkeypatch):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    monkeypatch.setenv("SPEK_SETTINGS_PATH", str(spek_dir / "settings.yaml"))
    SpekEnv.reset()
    settings = GlobalSettings.initialize()
    settings.sources["mywork"] = "/my/path"
    settings.save()
    reloaded = GlobalSettings.initialize()
    assert reloaded.sources["mywork"] == "/my/path"
