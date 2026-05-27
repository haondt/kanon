from __future__ import annotations

import dataclasses
import io
import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, overload

import yaml
from pydantic import BaseModel
from spek.core.utils import deep_merge

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

T = TypeVar("T", bound=BaseModel)


def parse_yaml(text: str) -> dict[str, Any]:
    return yaml.safe_load(text) or {}


@overload
def load_yaml(path: Path) -> dict[str, Any]: ...
@overload
def load_yaml(path: Path, model: type[T]) -> T: ...
@overload
def load_yaml(path: Path, model: type[T], extra: dict[str, Any]) -> T: ...

def load_yaml(path: Path, model: type[T] | None = None, extra: dict[str, Any] | None = None) -> T | dict[str, Any]:
    data = parse_yaml(path.read_text())
    if extra is not None:
        data = deep_merge(data, extra)
    if model is None:
        return data
    return model.model_validate(data)


def _literal_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    if "\n" in data or len(data) > 80:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _make_dumper() -> type[yaml.Dumper]:
    class _Dumper(yaml.Dumper):
        pass
    _Dumper.add_representer(str, _literal_representer)
    return _Dumper


def _normalize(data: Any) -> Any:
    if isinstance(data, Enum):
        return data.value
    if isinstance(data, dict):
        return {k: _normalize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_normalize(v) for v in data]
    return data


def _to_serializable(data: dict[str, Any] | BaseModel | Any) -> dict[str, Any]:
    if isinstance(data, BaseModel):
        return data.model_dump(mode="json", exclude_none=True, by_alias=True)
    if dataclasses.is_dataclass(data) and not isinstance(data, type):
        return _normalize(dataclasses.asdict(data))
    return _normalize(data)


def dump_yaml(data: dict[str, Any] | BaseModel) -> str:
    buf = io.StringIO()
    yaml.dump(_to_serializable(data), buf, Dumper=_make_dumper(), default_flow_style=False, sort_keys=False, allow_unicode=True)
    return buf.getvalue()


def save_yaml(data: dict[str, Any] | BaseModel, path: Path) -> None:
    path.write_text(dump_yaml(data))


def dump_json(data: dict[str, Any] | BaseModel, indent: int | None = None) -> str:
    return json.dumps(_to_serializable(data), indent=indent)


def save_json(data: dict[str, Any] | BaseModel, path: Path, indent: int = 2) -> None:
    path.write_text(dump_json(data, indent=indent) + "\n")
