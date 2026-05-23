from __future__ import annotations

from pathlib import Path

from spek.core.settings import GlobalSettings, SourceSpec, load_global_settings


def test_load_global_settings_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    result = load_global_settings()
    assert isinstance(result, GlobalSettings)
    assert result.sources == {}


def test_load_global_settings_parses_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "settings.yaml").write_text(
        "sources:\n  mywork:\n    path: /some/path\n"
    )
    result = load_global_settings()
    assert "mywork" in result.sources
    assert result.sources["mywork"].path == "/some/path"
    assert result.sources["mywork"].url is None
    assert result.sources["mywork"].ref is None


def test_load_global_settings_full_spec_round_trips(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "settings.yaml").write_text(
        "sources:\n  corp:\n    path: /corp/specs\n    url: https://example.com/specs.git\n    ref: main\n"
    )
    result = load_global_settings()
    spec = result.sources["corp"]
    assert spec.path == "/corp/specs"
    assert spec.url == "https://example.com/specs.git"
    assert spec.ref == "main"
