from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import KanonConfig
from kanon.core.errors import KanonKeyError, KanonValueError
from kanon.core.table import TableEdge, TableState, key_for, status_label


# ── core tests ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("index", "key"),
    [(0, "a"), (1, "b"), (25, "z"), (26, "aa"), (27, "ab"), (51, "az"), (52, "ba")],
)
def test_key_for(index, key):
    assert key_for(index) == key


def test_add_item_assigns_sequential_keys():
    state = TableState()
    assert state.add("One") == ("a", True)
    assert state.add("Two") == ("b", True)


def test_add_item_duplicate_title_is_noop():
    state = TableState()
    state.add("One")
    assert state.add("  one ") == ("a", False)
    assert len(state.items) == 1


def test_add_item_with_missing_link_raises():
    state = TableState()
    with pytest.raises(KanonKeyError, match="No item"):
        state.add("One", links=["z"])


def test_add_item_empty_title_raises():
    with pytest.raises(KanonValueError, match="empty"):
        TableState().add("  ")


def test_removed_keys_are_not_reused():
    state = TableState()
    state.add("One")
    state.remove_item("a")
    assert state.add("Two") == ("b", True)


def test_set_active_demotes_previous_active():
    state = TableState()
    state.add("One")
    state.add("Two")
    state.set_status("a", "active")
    assert state.set_status("b", "active") == "a"
    assert state.items["a"].status == "open"


def test_link_is_undirected_and_deduplicated():
    state = TableState()
    state.add("One")
    state.add("Two")
    assert state.link_items("b", "a") is True
    assert state.link_items("a", "b") is False
    assert state.neighbors("a") == ["b"]
    assert state.neighbors("b") == ["a"]


def test_link_to_self_raises():
    state = TableState()
    state.add("One")
    with pytest.raises(KanonValueError, match="itself"):
        state.link_items("a", "a")


def test_unlink_missing_edge_raises():
    state = TableState()
    state.add("One")
    state.add("Two")
    with pytest.raises(KanonValueError, match="not linked"):
        state.unlink_items("a", "b")


def test_remove_item_drops_edges():
    state = TableState()
    state.add("One")
    state.add("Two", links=["a"])
    state.remove_item("a")
    assert state.edges == []


def test_merge_unions_edges_without_self_loops():
    state = TableState()
    for title in ("One", "Two", "Three"):
        state.add(title)
    state.link_items("a", "b")
    state.link_items("b", "c")
    state.merge_items("a", "b")
    assert "b" not in state.items
    assert state.neighbors("a") == ["c"]


def test_merge_joins_summaries():
    state = TableState()
    state.add("One", "first")
    state.add("Two", "second")
    state.merge_items("a", "b")
    assert state.items["a"].summary == "first\n\nsecond"


@pytest.mark.parametrize(
    ("keep", "absorb", "expected"),
    [
        ("open", "open", "open"),
        ("open", "active", "active"),
        ("active", "open", "active"),
        ("resolved", "resolved", "resolved"),
        ("resolved", "open", "open"),
    ],
)
def test_merge_status_rule(keep, absorb, expected):
    state = TableState()
    state.add("One")
    state.add("Two")
    state.items["a"].status = keep
    state.items["b"].status = absorb
    state.merge_items("a", "b")
    assert state.items["a"].status == expected


def test_merge_into_self_raises():
    state = TableState()
    state.add("One")
    with pytest.raises(KanonValueError, match="itself"):
        state.merge_items("a", "a")


@pytest.mark.parametrize(
    ("status", "label"),
    [("open", "[  open  ]"), ("active", "[ active ]"), ("resolved", "[resolved]")],
)
def test_status_label_is_padded_inside_brackets(status, label):
    assert status_label(status) == label


def test_render_graph_empty():
    assert TableState().render_graph() == "Table is empty."


def test_render_graph_matches_design():
    state = TableState()
    for title in ("Session expiry", "Token storage", "Refresh rotation", "Cookie flags", "Rate limiting", "Log format"):
        state.add(title)
    for a, b in (("b", "d"), ("b", "c"), ("c", "a"), ("a", "b")):
        state.link_items(a, b)
    state.set_status("b", "active")
    state.set_status("d", "resolved")
    state.set_status("f", "resolved")
    assert state.render_graph() == (
        "6 items: 1 active · 3 open · 2 resolved\n"
        "\n"
        "● b  Token storage\n"
        "├─ ○ a  Session expiry\n"
        "│  └─ ○ c  Refresh rotation  ↔ b\n"
        "└─ ✓ d  Cookie flags\n"
        "\n"
        "○ e  Rate limiting\n"
        "\n"
        "✓ f  Log format"
    )


def test_lint_clean():
    state = TableState()
    state.add("One")
    assert state.lint() == []


def test_lint_flags_multiple_active_and_dangling_edge():
    state = TableState()
    state.add("One")
    state.add("Two")
    state.items["a"].status = "active"
    state.items["b"].status = "active"
    state.edges.append(TableEdge(a="a", b="z"))
    issues = state.lint()
    assert any("multiple active" in i for i in issues)
    assert any("missing item" in i for i in issues)


def test_table_roundtrip(tmp_path):
    KanonConfig.initialize(tmp_path)
    state = TableState()
    state.add("One", "summary")
    state.add("Two", links=["a"])
    state.save()
    loaded, _ = TableState.load()
    assert loaded == state


# ── CLI tests ─────────────────────────────────────────────────────────────────


def invoke(*args, project_root):
    return CliRunner().invoke(cli, ["--project-root", str(project_root), "table", *args])


def test_status_on_missing_file_is_empty(tmp_path):
    result = invoke("status", project_root=tmp_path)
    assert result.exit_code == 0
    assert "Table is empty." in result.output


def test_add_creates_file_and_prints_key(tmp_path):
    result = invoke("add", "One", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert "key: a" in result.output
    assert (tmp_path / ".kanon" / "table.yaml").exists()


def test_add_duplicate_title_is_noop(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("add", "one", project_root=tmp_path)
    assert result.exit_code == 0
    assert "no change" in result.output
    state, _ = TableState.load()
    assert len(state.items) == 1


def test_add_with_link(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    invoke("add", "Two", "--link", "a", project_root=tmp_path)
    state, _ = TableState.load()
    assert state.neighbors("b") == ["a"]


def test_add_reads_summary_from_stdin(tmp_path):
    result = CliRunner().invoke(
        cli,
        ["--project-root", str(tmp_path), "table", "add", "One", "--summary", "-"],
        input="line one\nline two\n",
    )
    assert result.exit_code == 0, result.output
    state, _ = TableState.load()
    assert state.items["a"].summary == "line one\nline two"


def test_set_status_reports_demoted_item(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    invoke("add", "Two", project_root=tmp_path)
    invoke("set-status", "a", "active", project_root=tmp_path)
    result = invoke("set-status", "b", "active", project_root=tmp_path)
    assert "demoted: a" in result.output


def test_set_status_rejects_unknown_status(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("set-status", "a", "done", project_root=tmp_path)
    assert result.exit_code != 0


def test_unknown_key_lists_valid_keys(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("remove", "z", project_root=tmp_path)
    assert result.exit_code == 1
    assert "Valid keys: a" in result.output


def test_status_key_shows_summary_and_neighbors(tmp_path):
    invoke("add", "One", "--summary", "about one", project_root=tmp_path)
    invoke("add", "Two", "--link", "a", project_root=tmp_path)
    result = invoke("status", "b", project_root=tmp_path)
    assert result.exit_code == 0
    assert "[  open  ]  b:{Two}" in result.output
    assert "[  open  ]  a:{One}" in result.output


def test_status_key_json(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    invoke("add", "Two", "--link", "a", project_root=tmp_path)
    data = json.loads(invoke("status", "b", "--json", project_root=tmp_path).output)
    assert data["neighbors"] == [{"key": "a", "title": "One", "status": "open"}]


def test_status_json_includes_items_and_edges(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    invoke("add", "Two", "--link", "a", project_root=tmp_path)
    data = json.loads(invoke("status", "--json", project_root=tmp_path).output)
    assert data["edges"] == [["a", "b"]]
    assert data["items"]["a"]["title"] == "One"


def test_merge_cli(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    invoke("add", "Two", project_root=tmp_path)
    result = invoke("merge", "a", "b", project_root=tmp_path)
    assert result.exit_code == 0
    state, _ = TableState.load()
    assert list(state.items) == ["a"]


def test_clear_removes_file(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("clear", project_root=tmp_path)
    assert result.exit_code == 0
    assert not (tmp_path / ".kanon" / "table.yaml").exists()


def test_edit_requires_a_field(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("edit", "a", project_root=tmp_path)
    assert result.exit_code == 1


def test_lint_cli_clean(tmp_path):
    invoke("add", "One", project_root=tmp_path)
    result = invoke("lint", project_root=tmp_path)
    assert "No issues found." in result.output
