from __future__ import annotations

import pytest
import yaml

from spek.core.plan import (
    PlanFile,
    PlanMeta,
    PlanStep,
    SplitEntry,
    SplitIndex,
    create_plan,
    create_split,
    load_plan,
    load_split_index,
    next_note_key,
    parse_plan_ref,
    save_plan,
    save_split_index,
)


# ── parse_plan_ref ─────────────────────────────────────────────────────────────


def test_parse_plan_ref_bare():
    assert parse_plan_ref("myplan") == (None, "myplan")


def test_parse_plan_ref_split():
    assert parse_plan_ref("mysplit/myplan") == ("mysplit", "myplan")


def test_parse_plan_ref_too_many_slashes():
    with pytest.raises(ValueError):
        parse_plan_ref("a/b/c")


# ── PlanFile round-trip ────────────────────────────────────────────────────────


def test_plan_file_roundtrip(tmp_path):
    plan = PlanFile(goal="Build something")
    plan.steps["s1"] = PlanStep(text="First step")
    plan.notes["pn1"] = "A note"
    plan._meta = PlanMeta(next_key={"pn": 2})

    save_plan(plan, tmp_path, "myplan")
    loaded, h = load_plan(tmp_path, "myplan")

    assert loaded.goal == "Build something"
    assert loaded.steps["s1"].text == "First step"
    assert loaded.steps["s1"].done is False
    assert loaded.notes["pn1"] == "A note"
    assert loaded._meta.next_key == {"pn": 2}


def test_plan_file_roundtrip_subplan(tmp_path):
    create_split("Split goal", tmp_path, "mysplit")
    plan = PlanFile(goal="Sub-plan goal")
    plan.steps["s1"] = PlanStep(text="A step")

    save_plan(plan, tmp_path, "mysplit/myplan")
    loaded, _ = load_plan(tmp_path, "mysplit/myplan")

    assert loaded.goal == "Sub-plan goal"
    assert loaded.steps["s1"].text == "A step"


# ── create_plan ────────────────────────────────────────────────────────────────


def test_create_plan_creates_file(tmp_path):
    plan, h = create_plan("My goal", tmp_path, "newplan")
    assert (tmp_path / ".spek" / "plans" / "newplan.yaml").exists()
    assert plan.goal == "My goal"


def test_create_plan_fails_if_exists(tmp_path):
    create_plan("Goal", tmp_path, "dup")
    with pytest.raises(FileExistsError):
        create_plan("Goal 2", tmp_path, "dup")


# ── SplitIndex round-trip ──────────────────────────────────────────────────────


def test_split_index_roundtrip(tmp_path):
    index = SplitIndex(goal="The big picture")
    index.plans["part1"] = SplitEntry(status="pending")
    index.plans["part2"] = SplitEntry(status="in_progress")

    save_split_index(index, tmp_path, "mysplit")
    loaded, _ = load_split_index(tmp_path, "mysplit")

    assert loaded.goal == "The big picture"
    assert loaded.plans["part1"].status == "pending"
    assert loaded.plans["part2"].status == "in_progress"


def test_create_split_creates_index(tmp_path):
    index, h = create_split("Split goal", tmp_path, "newsplit")
    assert (tmp_path / ".spek" / "plans" / "newsplit" / "index.yaml").exists()
    assert index.goal == "Split goal"


def test_create_split_fails_if_exists(tmp_path):
    create_split("Goal", tmp_path, "dup")
    with pytest.raises(FileExistsError):
        create_split("Goal 2", tmp_path, "dup")


# ── next_note_key ──────────────────────────────────────────────────────────────


def test_next_note_key_increments():
    plan = PlanFile(goal="g")
    k1 = next_note_key(plan)
    k2 = next_note_key(plan)
    assert k1 == "pn1"
    assert k2 == "pn2"


def test_next_note_key_does_not_reuse_after_delete():
    plan = PlanFile(goal="g")
    k1 = next_note_key(plan)
    plan.notes[k1] = "note"
    del plan.notes[k1]
    k2 = next_note_key(plan)
    assert k2 == "pn2"
