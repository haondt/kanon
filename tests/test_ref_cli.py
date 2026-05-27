from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from spek.cli import cli
from spek.core.config import SpekEnv


def make_references(spek_repo: Path, entries: dict[str, str]) -> None:
    references_dir = spek_repo / "references"
    for name, content in entries.items():
        dest = references_dir.joinpath(*name.split("/")).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def make_project_references(project: Path, entries: dict[str, str]) -> None:
    references_dir = project / ".spek" / "project" / "references"
    for name, content in entries.items():
        dest = references_dir.joinpath(*name.split("/")).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def init_project(project: Path) -> None:
    spek_dir = project / ".spek"
    spek_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc1234", "integrations": ["claude"]},
        "modules": [],
    }
    (spek_dir / "spek.yaml").write_text(yaml.dump(data))


NAVBAR_CONTENT = """\
---
spek:
  description: "Simple Bulma navbar"
  keywords:
    - bulma
    - navbar
    - navigation
---
<nav class="navbar">...</nav>
"""

FORM_CONTENT = """\
---
spek:
  description: "Basic Bulma form"
  keywords:
    - bulma
    - form
    - input
---
<form>...</form>
"""

LOCAL_REF_CONTENT = """\
---
spek:
  description: "Local project button"
  keywords:
    - local
    - button
    - project
---
<button>local</button>
"""

OVERRIDE_CONTENT = """\
---
spek:
  description: "Overridden navbar (local)"
  keywords:
    - bulma
    - navbar
    - override
---
<nav>local override</nav>
"""


def invoke(args: list[str], project_root: Path) -> object:
    return CliRunner().invoke(cli, ["--project-root", str(project_root)] + args)


def test_search_returns_match(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "navbar"], tmp_path)
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_no_match(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "modal"], tmp_path)
    assert result.exit_code == 0
    assert "No references found" in result.output


def test_search_json_output(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {
        "frontend/bulma/navbar": NAVBAR_CONTENT,
        "frontend/bulma/form": FORM_CONTENT,
    })
    result = invoke(["ref", "search", "--json", "bulma"], tmp_path)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
    assert all("name" in r and "description" in r and "keywords" in r for r in data)
    names = [r["name"] for r in data]
    assert "frontend/bulma/navbar" in names
    assert "frontend/bulma/form" in names


def test_read_returns_content(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "read", "frontend/bulma/navbar"], tmp_path)
    assert result.exit_code == 0
    assert '<nav class="navbar">' in result.output
    assert "spek:" not in result.output


def test_read_missing_exits_nonzero(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {})
    result = invoke(["ref", "read", "frontend/bulma/missing"], tmp_path)
    assert result.exit_code != 0


def test_read_json_output(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "read", "--json", "frontend/bulma/navbar"], tmp_path)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "frontend/bulma/navbar"
    assert data["description"] == "Simple Bulma navbar"
    assert "navbar" in data["keywords"]
    assert '<nav class="navbar">' in data["content"]
    assert "spek:" not in data["content"]


def test_search_multi_term_and(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "--match-all", "bulma", "navbar"], tmp_path)
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_multi_term_and_no_match(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "--match-all", "bulma", "form"], tmp_path)
    assert result.exit_code == 0
    assert "No references found" in result.output


def test_search_multi_term_or_default(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "navbar", "form"], tmp_path)
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_ranking(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {
        "frontend/bulma/navbar": NAVBAR_CONTENT,
        "frontend/bulma/form": FORM_CONTENT,
    })
    result = invoke(["ref", "search", "--json", "bulma", "navbar"], tmp_path)
    assert result.exit_code == 0
    data = json.loads(result.output)
    names = [r["name"] for r in data]
    assert names[0] == "frontend/bulma/navbar"


def test_search_default_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    result = invoke(["ref", "search", "--json", "shared"], tmp_path)
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 10


def test_search_limit_override(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    result = invoke(["ref", "search", "--json", "-n", "3", "shared"], tmp_path)
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 3


def test_search_limit_unlimited(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    result = invoke(["ref", "search", "--json", "-n", "0", "shared"], tmp_path)
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 12


# ── Project source tests ──────────────────────────────────────────────────────

def test_search_finds_project_ref(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_project_references(project, {"components/button": LOCAL_REF_CONTENT})
    result = invoke(["ref", "search", "--json", "local"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "project::components/button"


def test_search_merges_project_and_spek(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_project_references(project, {"components/button": LOCAL_REF_CONTENT})
    result = invoke(["ref", "search", "--json", "bulma"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    names = [r["name"] for r in data]
    assert "frontend/bulma/navbar" in names
    assert "project::components/button" not in names


def test_search_project_and_spek_same_path_both_appear(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_project_references(project, {"frontend/bulma/navbar": OVERRIDE_CONTENT})
    result = invoke(["ref", "search", "--json", "navbar"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    names = [r["name"] for r in data]
    assert "frontend/bulma/navbar" in names
    assert "project::frontend/bulma/navbar" in names


def test_read_returns_project_ref(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_project_references(project, {"components/button": LOCAL_REF_CONTENT})
    result = invoke(["ref", "read", "--json", "project::components/button"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "project::components/button"
    assert "<button>local</button>" in data["content"]


def test_read_project_ref_by_qualified_name(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_project_references(project, {"frontend/bulma/navbar": OVERRIDE_CONTENT})
    result = invoke(["ref", "read", "--json", "project::frontend/bulma/navbar"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["description"] == "Overridden navbar (local)"
    assert "<nav>local override</nav>" in data["content"]


def test_read_spek_ref_when_project_has_same_path(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    project = tmp_path / "project"
    project.mkdir()
    init_project(project)
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_project_references(project, {"components/button": LOCAL_REF_CONTENT})
    result = invoke(["ref", "read", "--json", "frontend/bulma/navbar"], project)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["description"] == "Simple Bulma navbar"


def test_search_no_project_config_uses_spek_only(tmp_path, monkeypatch):
    monkeypatch.setenv("SPEK_REPO_PATH", str(tmp_path))
    SpekEnv.reset()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    result = invoke(["ref", "search", "--json", "navbar"], tmp_path)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["name"] == "frontend/bulma/navbar"
