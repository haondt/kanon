from __future__ import annotations

import json

import pytest
import yaml
from click.testing import CliRunner

from spek.cli import cli
from spek.core.session import (
    Finding,
    PlanSection,
    PlanStep,
    ReviewPass,
    SessionState,
    create_session,
    delete_session,
    lint_session,
    load_session,
    next_build_note_key,
    next_finding_key,
    next_pass_key,
    next_plan_note_key,
    save_session,
)


# ── model tests ───────────────────────────────────────────────────────────────


def test_session_state_strips_goal_whitespace():
    state = SessionState(goal="  hello  ")
    assert state.goal == "hello"


def test_plan_step_strips_text():
    step = PlanStep(text="  do something  ")
    assert step.text == "do something"


def test_finding_validates_status():
    f = Finding(text="x", status="open")
    assert f.status == "open"


def test_finding_strips_fix_note():
    f = Finding(text="x", fix_note="  note  ")
    assert f.fix_note == "note"


def test_finding_fix_note_none_stays_none():
    f = Finding(text="x", fix_note=None)
    assert f.fix_note is None


def test_session_roundtrip(tmp_path):
    state = SessionState(goal="My goal")
    state.plan.steps["s1"] = PlanStep(text="Step one")
    state.plan.notes["pn1"] = "A plan note"
    state.build.notes["bn1"] = "A build note"
    state.review["p1"] = ReviewPass(findings={"f1": Finding(text="A finding")})
    state.amendments.append("Changed scope")
    state.detours.append("Fixed typo")
    state._meta.next_key = {"pn": 2, "bn": 2, "f": 2, "p": 2}

    before, after = save_session(state, tmp_path)
    loaded, h = load_session(tmp_path)

    assert loaded.goal == "My goal"
    assert loaded.plan.steps["s1"].text == "Step one"
    assert loaded.plan.steps["s1"].done is False
    assert loaded.plan.notes["pn1"] == "A plan note"
    assert loaded.build.notes["bn1"] == "A build note"
    assert loaded.review["p1"].findings["f1"].text == "A finding"
    assert loaded.amendments == ["Changed scope"]
    assert loaded.detours == ["Fixed typo"]
    assert loaded._meta.next_key == {"pn": 2, "bn": 2, "f": 2, "p": 2}


def test_create_session_fails_if_exists(tmp_path):
    create_session("first", tmp_path)
    with pytest.raises(FileExistsError):
        create_session("second", tmp_path)


def test_delete_session_raises_if_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_session(tmp_path)


def test_lint_session_empty_goal(tmp_path):
    state = SessionState(goal="x")
    state.goal = ""
    issues = lint_session(state)
    assert any("goal" in i for i in issues)


def test_finding_rejects_invalid_status():
    import pytest
    with pytest.raises(Exception):
        Finding(text="t", status="bad")


def test_lint_session_clean():
    state = SessionState(goal="valid goal")
    assert lint_session(state) == []


def test_key_generation_increments(tmp_path):
    create_session("goal", tmp_path)
    state, _ = load_session(tmp_path)
    k1 = next_plan_note_key(state)
    k2 = next_plan_note_key(state)
    assert k1 == "pn1"
    assert k2 == "pn2"


def test_key_generation_does_not_reuse_after_delete(tmp_path):
    create_session("goal", tmp_path)
    state, _ = load_session(tmp_path)
    k1 = next_plan_note_key(state)
    state.plan.notes[k1] = "note"
    del state.plan.notes[k1]
    k2 = next_plan_note_key(state)
    assert k2 == "pn2"


# ── CLI tests ─────────────────────────────────────────────────────────────────


def invoke(*args, project_root):
    return CliRunner().invoke(cli, ["session", *args, "--project-root", str(project_root)])


def test_session_start_creates_file(tmp_path):
    result = invoke("start", "My goal", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert (tmp_path / ".spek" / "session.yaml").exists()


def test_session_start_fails_if_exists(tmp_path):
    invoke("start", "Goal one", project_root=tmp_path)
    result = invoke("start", "Goal two", project_root=tmp_path)
    assert result.exit_code != 0


def test_session_start_json_returns_hash_and_goal(tmp_path):
    result = CliRunner().invoke(cli, ["session", "start", "My goal", "--json", "--project-root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "hash" in data
    assert data["goal"] == "My goal"


def test_session_goal_reads_goal(tmp_path):
    invoke("start", "Read this", project_root=tmp_path)
    result = invoke("goal", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert "Read this" in result.output


def test_session_status_shows_summary(tmp_path):
    invoke("start", "Status test", project_root=tmp_path)
    result = invoke("status", project_root=tmp_path)
    assert result.exit_code == 0, result.output
    assert "Status test" in result.output


def test_session_status_full_json(tmp_path):
    invoke("start", "Full test", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "session", "status", "--full", "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["goal"] == "Full test"
    assert "plan" in data


def test_session_plan_add_step(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "session", "plan", "add-step", "s1", "First step", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0, result.output
    state, _ = load_session(tmp_path)
    assert "s1" in state.plan.steps
    assert state.plan.steps["s1"].text == "First step"


def test_session_plan_add_step_fails_on_duplicate_key(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "plan", "add-step", "s1", "First", "--project-root", str(tmp_path)])
    result = CliRunner().invoke(cli, ["session", "plan", "add-step", "s1", "Second", "--project-root", str(tmp_path)])
    assert result.exit_code != 0


def test_session_plan_check_and_uncheck(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "plan", "add-step", "s1", "Step", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "plan", "check", "s1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.plan.steps["s1"].done is True

    CliRunner().invoke(cli, ["session", "plan", "uncheck", "s1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.plan.steps["s1"].done is False


def test_session_plan_note_returns_key(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "session", "plan", "note", "A note", "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["key"] == "pn1"


def test_session_plan_unnote_removes_note(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "plan", "note", "A note", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "amend", "plan", "unnote", "pn1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert "pn1" not in state.plan.notes


def test_session_build_note_and_unnote(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "session", "build", "note", "Build note", "--json", "--project-root", str(tmp_path)
    ])
    data = json.loads(result.output)
    assert data["key"] == "bn1"

    CliRunner().invoke(cli, ["session", "build", "unnote", "bn1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert "bn1" not in state.build.notes


def test_session_detour_add(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "detour", "add", "Fixed typo", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert "Fixed typo" in state.detours


def test_session_stance_set_and_clear(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "stance", "set", "autonomous", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.stance == "autonomous"

    CliRunner().invoke(cli, ["session", "stance", "clear", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.stance is None


def test_session_review_start_returns_pass_key(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    result = CliRunner().invoke(cli, [
        "session", "review", "start", "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["pass_key"] == "p1"


def test_session_review_start_idempotent_when_empty(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    result = CliRunner().invoke(cli, [
        "session", "review", "start", "--json", "--project-root", str(tmp_path)
    ])
    data = json.loads(result.output)
    assert data["pass_key"] == "p1"


def test_session_review_add_finding(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    result = CliRunner().invoke(cli, [
        "session", "review", "add-finding", "p1", "Missing error handling",
        "--json", "--project-root", str(tmp_path)
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["finding_key"] == "f1"
    assert data["count"] == 1


def test_session_review_finding_keys_global_across_passes(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "add-finding", "p1", "Finding 1", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "add-finding", "p1", "Finding 2", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    result = CliRunner().invoke(cli, [
        "session", "review", "add-finding", "p2", "Finding 3",
        "--json", "--project-root", str(tmp_path)
    ])
    data = json.loads(result.output)
    assert data["finding_key"] == "f3"


def test_session_review_close_and_reopen_finding(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "add-finding", "p1", "A finding", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "close-finding", "p1", "f1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.review["p1"].findings["f1"].status == "closed"

    CliRunner().invoke(cli, ["session", "review", "reopen-finding", "p1", "f1", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.review["p1"].findings["f1"].status == "reopened"


def test_session_review_set_fix_note(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "review", "start", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "review", "add-finding", "p1", "A finding", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, [
        "session", "review", "set-fix-note", "p1", "f1", "Fixed it",
        "--project-root", str(tmp_path)
    ])
    state, _ = load_session(tmp_path)
    assert state.review["p1"].findings["f1"].fix_note == "Fixed it"


def test_session_amend_goal(tmp_path):
    invoke("start", "Original goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "amend", "goal", "New goal", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.goal == "New goal"


def test_session_amend_plan_step(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "plan", "add-step", "s1", "Old text", "--project-root", str(tmp_path)])
    CliRunner().invoke(cli, ["session", "amend", "plan", "step", "s1", "New text", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert state.plan.steps["s1"].text == "New text"


def test_session_amend_add_note(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    CliRunner().invoke(cli, ["session", "amend", "add-note", "Changed scope", "--project-root", str(tmp_path)])
    state, _ = load_session(tmp_path)
    assert "Changed scope" in state.amendments


def test_session_lint_clean(tmp_path):
    invoke("start", "Valid goal", project_root=tmp_path)
    result = invoke("lint", project_root=tmp_path)
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_session_clear_deletes_file(tmp_path):
    invoke("start", "Goal", project_root=tmp_path)
    result = invoke("clear", project_root=tmp_path)
    assert result.exit_code == 0
    assert not (tmp_path / ".spek" / "session.yaml").exists()


def test_session_clear_fails_if_no_file(tmp_path):
    result = invoke("clear", project_root=tmp_path)
    assert result.exit_code != 0


def test_session_no_file_exits_with_error(tmp_path):
    result = invoke("goal", project_root=tmp_path)
    assert result.exit_code != 0
