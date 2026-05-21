from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from spek.cli import cli


def make_references(root: Path, entries: dict[str, str]) -> None:
    references_dir = root / "references"
    for name, content in entries.items():
        dest = references_dir.joinpath(*name.split("/")).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


def make_local_references(project_root: Path, entries: dict[str, str]) -> None:
    local_dir = project_root / ".spek" / "local" / "references"
    for name, content in entries.items():
        dest = local_dir.joinpath(*name.split("/")).with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)


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


def test_search_returns_match(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "navbar"])
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_no_match(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "modal"])
    assert result.exit_code == 0
    assert "No references found" in result.output


def test_search_json_output(tmp_path):
    make_references(tmp_path, {
        "frontend/bulma/navbar": NAVBAR_CONTENT,
        "frontend/bulma/form": FORM_CONTENT,
    })
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "bulma"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
    assert all("name" in r and "description" in r and "keywords" in r for r in data)
    names = [r["name"] for r in data]
    assert "frontend/bulma/navbar" in names
    assert "frontend/bulma/form" in names


def test_read_returns_content(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "read", "frontend/bulma/navbar"])
    assert result.exit_code == 0
    assert '<nav class="navbar">' in result.output
    assert "spek:" not in result.output


def test_read_missing_exits_nonzero(tmp_path):
    make_references(tmp_path, {})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "read", "frontend/bulma/missing"])
    assert result.exit_code != 0


def test_read_json_output(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "read", "--json", "frontend/bulma/navbar"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "frontend/bulma/navbar"
    assert data["description"] == "Simple Bulma navbar"
    assert "navbar" in data["keywords"]
    assert '<nav class="navbar">' in data["content"]
    assert "spek:" not in data["content"]


def test_search_multi_term_and(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "bulma", "navbar"])
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_multi_term_and_no_match(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "bulma", "form"])
    assert result.exit_code == 0
    assert "No references found" in result.output


def test_search_multi_term_match_any(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "navbar", "form", "--match-any"])
    assert result.exit_code == 0
    assert "frontend/bulma/navbar" in result.output


def test_search_ranking(tmp_path):
    make_references(tmp_path, {
        "frontend/bulma/navbar": NAVBAR_CONTENT,
        "frontend/bulma/form": FORM_CONTENT,
    })
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "bulma", "navbar", "--match-any"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    names = [r["name"] for r in data]
    assert names[0] == "frontend/bulma/navbar"  # matches both terms; form matches only bulma


def test_search_default_limit(tmp_path):
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "shared"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 10


def test_search_limit_override(tmp_path):
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "-n", "3", "shared"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 3


def test_search_limit_unlimited(tmp_path):
    entries = {f"entry/item{i:02d}": f"---\nspek:\n  description: \"Item {i}\"\n  keywords:\n    - shared\n---\ncontent\n" for i in range(12)}
    make_references(tmp_path, entries)
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "-n", "0", "shared"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 12


# ── Local reference tests ─────────────────────────────────────────────────────

def test_search_finds_local_ref(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_local_references(project, {"components/button": LOCAL_REF_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "local"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["name"] == "components/button"


def test_search_merges_local_and_upstream(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_local_references(project, {"components/button": LOCAL_REF_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "bulma", "--match-any"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    names = [r["name"] for r in data]
    assert "frontend/bulma/navbar" in names
    assert "components/button" not in names  # no bulma keyword


def test_search_local_shadows_upstream(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_local_references(project, {"frontend/bulma/navbar": OVERRIDE_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "navbar"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["description"] == "Overridden navbar (local)"


def test_read_returns_local_ref(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_local_references(project, {"components/button": LOCAL_REF_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "read", "--json", "components/button"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "components/button"
    assert "<button>local</button>" in data["content"]


def test_read_local_shadows_upstream(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_local_references(project, {"frontend/bulma/navbar": OVERRIDE_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "read", "--json", "frontend/bulma/navbar"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["description"] == "Overridden navbar (local)"
    assert "<nav>local override</nav>" in data["content"]


def test_read_falls_back_to_upstream(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    make_local_references(project, {"components/button": LOCAL_REF_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=project):
        result = CliRunner().invoke(cli, ["ref", "read", "--json", "frontend/bulma/navbar"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["description"] == "Simple Bulma navbar"


def test_search_no_local_project_uses_upstream_only(tmp_path):
    make_references(tmp_path, {"frontend/bulma/navbar": NAVBAR_CONTENT})
    with patch("spek.commands.ref.spek_repo_path", return_value=tmp_path), \
         patch("spek.commands.ref.local_project_path", return_value=None):
        result = CliRunner().invoke(cli, ["ref", "search", "--json", "navbar"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["name"] == "frontend/bulma/navbar"
