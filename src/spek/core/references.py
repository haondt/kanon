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


def _local_references_dir(project_root: Path | None) -> Path | None:
    if project_root is None:
        return None
    d = project_root / ".spek" / "local" / "references"
    return d if d.exists() else None


def list_references(repo_path: Path, project_root: Path | None = None) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    local_dir = _local_references_dir(project_root)
    if local_dir:
        for src in sorted(local_dir.rglob("*.md")):
            name = str(src.relative_to(local_dir).with_suffix(""))
            seen.add(name)
            results.append(name)
    upstream_dir = repo_path / "references"
    if upstream_dir.exists():
        for src in sorted(upstream_dir.rglob("*.md")):
            name = str(src.relative_to(upstream_dir).with_suffix(""))
            if name not in seen:
                results.append(name)
    return results


def _score_dir(ref_dir: Path, terms: list[str], match_all: bool) -> list[tuple[int, ReferenceResult]]:
    scored: list[tuple[int, ReferenceResult]] = []
    for src in sorted(ref_dir.rglob("*.md")):
        name = str(src.relative_to(ref_dir).with_suffix(""))
        meta, _ = parse_reference_frontmatter(src.read_text())
        kws = [kw.lower() for kw in meta.spek.keywords]
        match_count = sum(1 for t in terms if any(t in kw for kw in kws))
        if match_all and match_count < len(terms):
            continue
        if not match_all and match_count == 0:
            continue
        scored.append((match_count, ReferenceResult(
            name=name,
            description=meta.spek.description,
            keywords=meta.spek.keywords,
        )))
    return scored


def search_references(repo_path: Path, terms: list[str], match_all: bool = True, project_root: Path | None = None) -> list[ReferenceResult]:
    lowered_terms = [t.lower() for t in terms]
    seen: set[str] = set()
    scored: list[tuple[int, ReferenceResult]] = []

    local_dir = _local_references_dir(project_root)
    if local_dir:
        for score, result in _score_dir(local_dir, lowered_terms, match_all):
            seen.add(result.name)
            scored.append((score, result))

    upstream_dir = repo_path / "references"
    if upstream_dir.exists():
        for score, result in _score_dir(upstream_dir, lowered_terms, match_all):
            if result.name not in seen:
                scored.append((score, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]


def read_reference(repo_path: Path, name: str, project_root: Path | None = None) -> ReferenceResult:
    local_dir = _local_references_dir(project_root)
    if local_dir:
        local_path = local_dir.joinpath(*name.split("/")).with_suffix(".md")
        if local_path.exists():
            meta, body = parse_reference_frontmatter(local_path.read_text())
            return ReferenceResult(
                name=name,
                description=meta.spek.description,
                keywords=meta.spek.keywords,
                content=body,
            )
    upstream_path = (repo_path / "references").joinpath(*name.split("/")).with_suffix(".md")
    if not upstream_path.exists():
        raise FileNotFoundError(f"Reference '{name}' not found")
    meta, body = parse_reference_frontmatter(upstream_path.read_text())
    return ReferenceResult(
        name=name,
        description=meta.spek.description,
        keywords=meta.spek.keywords,
        content=body,
    )
