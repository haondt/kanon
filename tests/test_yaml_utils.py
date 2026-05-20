from pathlib import Path

import pytest
from pydantic import BaseModel

from spek.core.yaml_utils import load_yaml, save_yaml


class _Sample(BaseModel):
    name: str
    tags: list[str] = []
    optional: str | None = None


def test_load_yaml_as_dict(tmp_path):
    (tmp_path / "f.yaml").write_text("name: hello\ntags:\n  - a\n")
    result = load_yaml(tmp_path / "f.yaml")
    assert result == {"name": "hello", "tags": ["a"]}


def test_load_yaml_as_model(tmp_path):
    (tmp_path / "f.yaml").write_text("name: hello\ntags:\n  - a\n  - b\n")
    result = load_yaml(tmp_path / "f.yaml", _Sample)
    assert isinstance(result, _Sample)
    assert result.name == "hello"
    assert result.tags == ["a", "b"]


def test_load_yaml_model_validation_error(tmp_path):
    from pydantic import ValidationError
    (tmp_path / "f.yaml").write_text("tags:\n  - a\n")  # missing required 'name'
    with pytest.raises(ValidationError):
        load_yaml(tmp_path / "f.yaml", _Sample)


def test_save_yaml_model_excludes_none(tmp_path):
    model = _Sample(name="hi", optional=None)
    path = tmp_path / "out.yaml"
    save_yaml(model, path)
    assert "optional" not in path.read_text()
    assert "name: hi" in path.read_text()


def test_save_yaml_roundtrip(tmp_path):
    path = tmp_path / "f.yaml"
    model = _Sample(name="hello", tags=["x", "y"])
    save_yaml(model, path)
    reloaded = load_yaml(path, _Sample)
    assert reloaded == model
