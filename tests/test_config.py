from spek.core.config import SpekConfig, SpekMeta


def _minimal_config() -> SpekConfig:
    return SpekConfig(
        meta=SpekMeta(spek_version="0.1.0", spek_sha="abc1234", integrations=["claude"]),
        modules=["git/commit-style"],
    )


def test_config_roundtrip(tmp_path):
    path = tmp_path / "spek.yaml"
    config = _minimal_config()
    config.save(path)
    loaded = SpekConfig.load(path)
    assert loaded == config


def test_config_save_omits_empty_lists(tmp_path):
    path = tmp_path / "spek.yaml"
    _minimal_config().save(path)
    text = path.read_text()
    assert "stances" not in text
    assert "local_modules" not in text
    assert "local_stances" not in text


def test_config_save_omits_null_profile(tmp_path):
    path = tmp_path / "spek.yaml"
    _minimal_config().save(path)
    assert "profile" not in path.read_text()
