from pathlib import Path
from kanon.core.config import Integration, KanonConfig, KanonMeta


def _minimal_config() -> KanonConfig:
    return KanonConfig(
        meta=KanonMeta(kanon_version="0.1.0", kanon_sha="abc1234", integrations=[Integration.CLAUDE]),
        kanons=["git/commit-style"],
    )


def _setup(tmp_path: Path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    KanonConfig.initialize(tmp_path)
    return kanon_dir


def test_config_roundtrip(tmp_path: Path):
    kanon_dir = _setup(tmp_path)
    config = _minimal_config()
    config.save()
    loaded = KanonConfig.load(kanon_dir / "kanon.yaml")
    assert loaded == config


def test_config_save_empty_lists(tmp_path: Path):
    kanon_dir = _setup(tmp_path)
    _minimal_config().save()
    loaded = KanonConfig.load(kanon_dir / "kanon.yaml")
    assert loaded.stances == []


def test_config_save_omits_null_profile(tmp_path: Path):
    kanon_dir = _setup(tmp_path)
    _minimal_config().save()
    assert "profile" not in (kanon_dir / "kanon.yaml").read_text()
