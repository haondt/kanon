from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ListItemEntry(BaseModel):
    kind: Literal["list_item"] = "list_item"
    path: list[str]
    value: Any = None


class ScalarEntry(BaseModel):
    kind: Literal["scalar"] = "scalar"
    path: list[str]
    had_prior: bool
    prior: Any = None
    written: Any = None


JsonEntry = Annotated[ListItemEntry | ScalarEntry, Field(discriminator="kind")]


BlobKind = Literal["directory", "file"]


class BlobEntry(BaseModel):
    """A path kanon owns wholesale, as opposed to keys merged into a file."""

    kind: BlobKind


class IntegrationLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    json_files: dict[str, list[JsonEntry]] = Field(default_factory=dict)
    blobs: dict[str, BlobEntry] = Field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.json_files and not self.blobs
