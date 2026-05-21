from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from spek.core.yaml_utils import FRONTMATTER_RE, parse_yaml


class _ReferenceMeta(BaseModel):
    description: str | None = None
    keywords: list[str] = []


class ReferenceFrontmatter(BaseModel):
    spek: _ReferenceMeta = _ReferenceMeta()


class ReferenceResult(BaseModel):
    name: str
    description: str | None
    keywords: list[str]
    content: str | None = None


def parse_reference_frontmatter(content: str) -> tuple[ReferenceFrontmatter, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return ReferenceFrontmatter(), content
    data: dict[str, Any] = parse_yaml(match.group(1))
    return ReferenceFrontmatter.model_validate(data), content[match.end():]


def list_references(repo_path: Path) -> list[str]:
    references_dir = repo_path / "references"
    if not references_dir.exists():
        return []
    results: list[str] = []
    for src in sorted(references_dir.rglob("*.md")):
        results.append(str(src.relative_to(references_dir).with_suffix("")))
    return results


def search_references(repo_path: Path, query: str) -> list[ReferenceResult]:
    references_dir = repo_path / "references"
    q = query.lower()
    results: list[ReferenceResult] = []
    for name in list_references(repo_path):
        path = references_dir.joinpath(*name.split("/")).with_suffix(".md")
        meta, _ = parse_reference_frontmatter(path.read_text())
        if any(q in kw.lower() for kw in meta.spek.keywords):
            results.append(ReferenceResult(
                name=name,
                description=meta.spek.description,
                keywords=meta.spek.keywords,
            ))
    return results


def read_reference(repo_path: Path, name: str) -> ReferenceResult:
    references_dir = repo_path / "references"
    path = references_dir.joinpath(*name.split("/")).with_suffix(".md")
    if not path.exists():
        raise FileNotFoundError(f"Reference '{name}' not found")
    meta, body = parse_reference_frontmatter(path.read_text())
    return ReferenceResult(
        name=name,
        description=meta.spek.description,
        keywords=meta.spek.keywords,
        content=body,
    )
