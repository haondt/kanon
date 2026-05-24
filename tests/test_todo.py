from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from spek.cli import cli
from spek.core.todo import (
    TodoSection,
    TodoState,
    create_todo,
    lint_todo,
    load_todo,
    save_todo,
)


# ── model tests ───────────────────────────────────────────────────────────────


def test_todo_section_strips_name():
    s = TodoSection(name="  My Section  ")
    assert s.name == "My Section"


def test_todo_section_strips_items():
    s = TodoSection(name="x", items=["  item  ", "  other  "])
    assert s.items == ["item", "other"]


def test_todo_roundtrip(tmp_path):
    state = TodoState(sections={
        "cat1": TodoSection(name="Category 1", items=["Do thing A", "Do thing B"]),
        "cat2": TodoSection(name="Category 2", items=["Do thing C"]),
    })
    save_todo(state, tmp_path)
    loaded, h = load_todo(tmp_path)
    assert loaded.sections["cat1"].name == "Category 1"
    assert loaded.sections["cat1"].items == ["Do thing A", "Do thing B"]
    assert loaded.sections["cat2"].items == ["Do thing C"]


def test_create_todo_fails_if_exists(tmp_path):
    create_todo(tmp_path)
    with pytest.raises(FileExistsError):
        create_todo(tmp_path)


def test_lint_todo_empty_section_name(tmp_path):
    state = TodoState(sections={"k": TodoSection(name="x")})
    state.sections["k"].name = ""
    issues = lint_todo(state)
    assert any("empty name" in i for i in issues)


def test_lint_todo_empty_item(tmp_path):
    state = TodoState(sections={"k": TodoSection(name="Cat", items=[""])})
    issues = lint_todo(state)
    assert any("empty item" in i for i in issues)


def test_lint_todo_clean():
    state = TodoState(sections={"k": TodoSection(name="Cat", items=["Do thing"])})
    assert lint_todo(state) == []


# ── CLI tests ─────────────────────────────────────────────────────────────────


def invoke(*args, project_root):
    return CliRunner().invoke(cli, ["todo", *args, "--project-root", str(project_root)])


def _bootstrap(tmp_path, section_key="cat", section_name="Category"):
    invoke("section", "add", section_key, section_name, project_root=tmp_path)


def test_todo_section_add_creates_file(tmp_path):
    result = invoke("section", "add", "cat", "Category", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert (tmp_path / ".spek" / "todo.yaml").exists()


def test_todo_section_add_fails_on_duplicate(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("section", "add", "cat", "Other", project_root=tmp_path)
    assert result.exit_code != 0


def test_todo_section_add_allow_exists_is_noop(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("section", "add", "--allow-exists", "cat", "Other", project_root=tmp_path)
    assert result.exit_code == 0
    state, _ = load_todo(tmp_path)
    assert state.sections["cat"].name == "Category"


def test_todo_section_status(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("section", "status", project_root=tmp_path)
    assert result.exit_code == 0
    assert "cat" in result.output or "Category" in result.output


def test_todo_section_search(tmp_path):
    _bootstrap(tmp_path, "cat", "My Category")
    result = invoke("section", "search", "my", project_root=tmp_path)
    assert result.exit_code == 0
    assert "My Category" in result.output


def test_todo_add_item(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("add", "Do the thing", "--section", "cat", project_root=tmp_path)
    assert result.exit_code == 0
    state, _ = load_todo(tmp_path)
    assert "Do the thing" in state.sections["cat"].items


def test_todo_add_fails_unknown_section(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("add", "Item", "--section", "missing", project_root=tmp_path)
    assert result.exit_code != 0


def test_todo_remove_item(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Do the thing", "--section", "cat", project_root=tmp_path)
    result = invoke("remove", "Do the thing", "--section", "cat", project_root=tmp_path)
    assert result.exit_code == 0
    state, _ = load_todo(tmp_path)
    assert "cat" not in state.sections


def test_todo_remove_auto_deletes_empty_section(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Only item", "--section", "cat", project_root=tmp_path)
    invoke("remove", "Only item", "--section", "cat", project_root=tmp_path)
    state, _ = load_todo(tmp_path)
    assert "cat" not in state.sections


def test_todo_remove_fails_if_item_not_found(tmp_path):
    _bootstrap(tmp_path)
    result = invoke("remove", "Nonexistent item", "--section", "cat", project_root=tmp_path)
    assert result.exit_code != 0


def test_todo_status_shows_items(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Item one", "--section", "cat", project_root=tmp_path)
    result = invoke("status", project_root=tmp_path)
    assert result.exit_code == 0
    assert "Item one" in result.output


def test_todo_status_json(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Item one", "--section", "cat", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "todo", "status", "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "hash" in data
    assert "sections" in data


def test_todo_status_section_filter(tmp_path):
    _bootstrap(tmp_path, "cat1", "Cat 1")
    invoke("section", "add", "cat2", "Cat 2", project_root=tmp_path)
    invoke("add", "Item in cat1", "--section", "cat1", project_root=tmp_path)
    invoke("add", "Item in cat2", "--section", "cat2", project_root=tmp_path)
    result = invoke("status", "--section", "cat1", project_root=tmp_path)
    assert "Item in cat1" in result.output
    assert "Item in cat2" not in result.output


def test_todo_search_all_terms_must_match(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Fix the database bug", "--section", "cat", project_root=tmp_path)
    invoke("add", "Fix the UI bug", "--section", "cat", project_root=tmp_path)
    result = invoke("search", "fix", "database", project_root=tmp_path)
    assert result.exit_code == 0
    assert "Fix the database bug" in result.output
    assert "Fix the UI bug" not in result.output


def test_todo_search_json(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "Fix the bug", "--section", "cat", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "todo", "search", "bug", "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "sections" in data


def test_todo_lint_clean(tmp_path):
    _bootstrap(tmp_path)
    invoke("add", "An item", "--section", "cat", project_root=tmp_path)
    result = invoke("lint", project_root=tmp_path)
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_todo_no_file_exits_with_error(tmp_path):
    result = invoke("status", project_root=tmp_path)
    assert result.exit_code != 0
