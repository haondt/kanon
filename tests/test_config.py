from spek.core.config import SpekConfig, SpekMeta


def _minimal_config() -> SpekConfig:
    return SpekConfig(
        meta=SpekMeta(spek_version="0.1.0", spek_sha="abc1234", integrations=["claude"]),
        modules=["git/commit-style"],
    )


def _setup(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    SpekConfig.initialize(tmp_path)
    return spek_dir


def test_config_roundtrip(tmp_path):
    spek_dir = _setup(tmp_path)
    config = _minimal_config()
    config.save()
    loaded = SpekConfig.load(spek_dir / "spek.yaml")
    assert loaded == config


def test_config_save_empty_lists(tmp_path):
    spek_dir = _setup(tmp_path)
    _minimal_config().save()
    loaded = SpekConfig.load(spek_dir / "spek.yaml")
    assert loaded.stances == []
    assert loaded.local_modules == []
    assert loaded.local_stances == []


def test_config_save_omits_null_profile(tmp_path):
    spek_dir = _setup(tmp_path)
    _minimal_config().save()
    assert "profile" not in (spek_dir / "spek.yaml").read_text()
