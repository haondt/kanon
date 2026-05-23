from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, overload

import yaml
from pydantic import BaseModel

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

T = TypeVar("T", bound=BaseModel)


def parse_yaml(text: str) -> dict[str, Any]:
    return yaml.safe_load(text) or {}


@overload
def load_yaml(path: Path) -> dict[str, Any]: ...
@overload
def load_yaml(path: Path, model: type[T]) -> T: ...

def load_yaml(path: Path, model: type[T] | None = None) -> T | dict[str, Any]:
    data = parse_yaml(path.read_text())
    if model is None:
        return data
    return model.model_validate(data)


def _literal_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    if "\n" in data or len(data) > 80:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _enum_str_representer(dumper: yaml.Dumper, data: Enum) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.value)


def _make_dumper(*enum_types: type) -> type[yaml.Dumper]:
    class _Dumper(yaml.Dumper):
        pass
    _Dumper.add_representer(str, _literal_representer)
    for enum_type in enum_types:
        _Dumper.add_representer(enum_type, _enum_str_representer)
    return _Dumper


def dump_yaml(data: dict[str, Any] | BaseModel) -> str:
    if isinstance(data, BaseModel):
        data = data.model_dump(exclude_defaults=True)
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def save_yaml(data: dict[str, Any] | BaseModel, path: Path) -> None:
    path.write_text(dump_yaml(data))
