from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from spek.cli import cli
from spek.core.plan import (
    create_plan,
    create_split,
    load_plan,
    load_split_index,
)


def invoke(*args, project_root):
    return CliRunner().invoke(cli, [*args, "--project-root", str(project_root)])


# ── spek plan create ───────────────────────────────────────────────────────────


def test_plan_create(tmp_path):
    result = invoke("plan", "create", "myplan", "Do something", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert (tmp_path / ".spek" / "plans" / "myplan.yaml").exists()


def test_plan_create_json(tmp_path):
    result = CliRunner().invoke(cli, ["plan", "create", "myplan", "Goal", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "hash" in data
    assert data["goal"] == "Goal"


def test_plan_create_fails_if_exists(tmp_path):
    invoke("plan", "create", "dup", "Goal", project_root=tmp_path)
    result = invoke("plan", "create", "dup", "Goal 2", project_root=tmp_path)
    assert result.exit_code != 0


def test_plan_create_subplan_registers_in_index(tmp_path):
    invoke("split", "create", "mysplit", "Split goal", project_root=tmp_path)
    invoke("plan", "create", "mysplit/part1", "Part one", project_root=tmp_path)
    index, _ = load_split_index(tmp_path, "mysplit")
    assert "part1" in index.plans
    assert index.plans["part1"].status == "pending"


def test_plan_create_subplan_fails_if_split_missing(tmp_path):
    result = invoke("plan", "create", "nosuchsplit/part1", "Goal", project_root=tmp_path)
    assert result.exit_code != 0


# ── spek plan read ─────────────────────────────────────────────────────────────


def test_plan_read(tmp_path):
    create_plan("Read me", tmp_path, "myplan")
    result = invoke("plan", "read", "myplan", project_root=tmp_path)
    assert result.exit_code == 0
    assert "Read me" in result.output


def test_plan_read_json(tmp_path):
    create_plan("Read me", tmp_path, "myplan")
    result = CliRunner().invoke(cli, ["plan", "read", "myplan", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["goal"] == "Read me"
    assert "steps" in data
    assert "notes" in data


def test_plan_read_missing_fails(tmp_path):
    result = invoke("plan", "read", "nope", project_root=tmp_path)
    assert result.exit_code != 0


# ── spek plan add-step / edit-step / remove-step ──────────────────────────────


def test_plan_add_step(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = invoke("plan", "add-step", "myplan", "s1", "First step", project_root=tmp_path)
    assert result.exit_code == 0
    plan, _ = load_plan(tmp_path, "myplan")
    assert "s1" in plan.steps
    assert plan.steps["s1"].text == "First step"


def test_plan_add_step_fails_on_duplicate(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    invoke("plan", "add-step", "myplan", "s1", "First", project_root=tmp_path)
    result = invoke("plan", "add-step", "myplan", "s1", "Second", project_root=tmp_path)
    assert result.exit_code != 0


def test_plan_edit_step(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    invoke("plan", "add-step", "myplan", "s1", "Old text", project_root=tmp_path)
    result = invoke("plan", "edit-step", "myplan", "s1", "New text", project_root=tmp_path)
    assert result.exit_code == 0
    plan, _ = load_plan(tmp_path, "myplan")
    assert plan.steps["s1"].text == "New text"


def test_plan_edit_step_fails_if_missing(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = invoke("plan", "edit-step", "myplan", "nope", "Text", project_root=tmp_path)
    assert result.exit_code != 0


def test_plan_remove_step(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    invoke("plan", "add-step", "myplan", "s1", "A step", project_root=tmp_path)
    result = invoke("plan", "remove-step", "myplan", "s1", project_root=tmp_path)
    assert result.exit_code == 0
    plan, _ = load_plan(tmp_path, "myplan")
    assert "s1" not in plan.steps


def test_plan_remove_step_fails_if_missing(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = invoke("plan", "remove-step", "myplan", "nope", project_root=tmp_path)
    assert result.exit_code != 0


# ── spek plan note / edit-note / remove-note ──────────────────────────────────


def test_plan_note_auto_keys(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = CliRunner().invoke(cli, ["plan", "note", "myplan", "First note", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["key"] == "pn1"


def test_plan_edit_note(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    invoke("plan", "note", "myplan", "Old note", project_root=tmp_path)
    result = invoke("plan", "edit-note", "myplan", "pn1", "New note", project_root=tmp_path)
    assert result.exit_code == 0
    plan, _ = load_plan(tmp_path, "myplan")
    assert plan.notes["pn1"] == "New note"


def test_plan_edit_note_fails_if_missing(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = invoke("plan", "edit-note", "myplan", "pn99", "Text", project_root=tmp_path)
    assert result.exit_code != 0


def test_plan_remove_note(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    invoke("plan", "note", "myplan", "A note", project_root=tmp_path)
    result = invoke("plan", "remove-note", "myplan", "pn1", project_root=tmp_path)
    assert result.exit_code == 0
    plan, _ = load_plan(tmp_path, "myplan")
    assert "pn1" not in plan.notes


def test_plan_remove_note_fails_if_missing(tmp_path):
    create_plan("Goal", tmp_path, "myplan")
    result = invoke("plan", "remove-note", "myplan", "pn99", project_root=tmp_path)
    assert result.exit_code != 0


# ── spek split create / list / status ─────────────────────────────────────────


def test_split_create(tmp_path):
    result = invoke("split", "create", "mysplit", "Big goal", project_root=tmp_path)
    assert result.exit_code == 0
    assert (tmp_path / ".spek" / "plans" / "mysplit" / "index.yaml").exists()


def test_split_create_json(tmp_path):
    result = CliRunner().invoke(cli, ["split", "create", "mysplit", "Big goal", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["goal"] == "Big goal"


def test_split_create_fails_if_exists(tmp_path):
    invoke("split", "create", "dup", "Goal", project_root=tmp_path)
    result = invoke("split", "create", "dup", "Goal 2", project_root=tmp_path)
    assert result.exit_code != 0


def test_split_list(tmp_path):
    invoke("split", "create", "alpha", "Alpha goal", project_root=tmp_path)
    invoke("split", "create", "beta", "Beta goal", project_root=tmp_path)
    result = invoke("split", "list", project_root=tmp_path)
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_split_list_empty(tmp_path):
    result = invoke("split", "list", project_root=tmp_path)
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_split_list_json(tmp_path):
    invoke("split", "create", "mysplit", "Goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, ["split", "list", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["name"] == "mysplit"


def test_split_status(tmp_path):
    invoke("split", "create", "mysplit", "Big goal", project_root=tmp_path)
    invoke("plan", "create", "mysplit/p1", "Part one", project_root=tmp_path)
    result = invoke("split", "status", "mysplit", project_root=tmp_path)
    assert result.exit_code == 0
    assert "p1" in result.output
    assert "pending" in result.output


def test_split_status_json(tmp_path):
    invoke("split", "create", "mysplit", "Big goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, ["split", "status", "mysplit", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["goal"] == "Big goal"
    assert "plans" in data


def test_split_status_fails_if_missing(tmp_path):
    result = invoke("split", "status", "nope", project_root=tmp_path)
    assert result.exit_code != 0
