from __future__ import annotations

from dataclasses import dataclass

from kanon.core.config import SourcedResource
from kanon.core.yaml_utils import dump_yaml, parse_yaml


@dataclass
class Stance:
    description: str
    kanons: list[str]

    @property
    def kanons_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.kanons]

    def dump(self) -> str:
        data = {"description": self.description, "kanons": self.kanons}
        return dump_yaml(data)

    @classmethod
    def load(cls, content: str) -> Stance:
        data = parse_yaml(content)
        return cls(
            description=data.get("description", ""),
            kanons=SourcedResource.sanitize(data.get("kanons", [])),
        )
