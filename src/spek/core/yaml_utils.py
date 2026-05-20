from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, TypeVar, overload

from pydantic import BaseModel

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


def dump_yaml(data: dict[str, Any] | BaseModel) -> str:
    if isinstance(data, BaseModel):
        data = data.model_dump(exclude_none=True)
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def save_yaml(data: dict[str, Any] | BaseModel, path: Path) -> None:
    path.write_text(dump_yaml(data))
