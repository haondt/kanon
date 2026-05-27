from __future__ import annotations

from dataclasses import dataclass

from spek.core.config import SourcedResource
from spek.core.yaml_utils import dump_yaml, parse_yaml


@dataclass
class Stance:
    description: str
    modules: list[str]

    @property
    def modules_sr(self) -> list[SourcedResource]:
        return [SourcedResource.parse(r) for r in self.modules]

    def dump(self) -> str:
        data = {"description": self.description, "modules": self.modules}
        return dump_yaml(data)

    @classmethod
    def load(cls, content: str) -> Stance:
        data = parse_yaml(content)
        return cls(
            description=data.get("description", ""),
            modules=SourcedResource.sanitize(data.get("modules", [])),
        )
