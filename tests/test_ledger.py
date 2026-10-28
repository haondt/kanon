from __future__ import annotations

import json
from pathlib import Path

import pytest

from kanon.core.config import Integration
from kanon.core.ledger import BACKUP_SUFFIX, JsonFileError, Ledger, LedgerFileError


@pytest.fixture
def target(tmp_path: Path) -> Path:
    return tmp_path / "settings.json"


@pytest.fixture
def ledger(tmp_path: Path) -> Ledger:
    return Ledger.load(tmp_path / "ledger.json")


def _read(path: Path) -> dict:
    return json.loads(path.read_text())


def test_apply_creates_missing_target(target, ledger):
    ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})

    assert _read(target) == {"includeGitInstructions": False}


def test_apply_preserves_user_keys(target, ledger):
    target.write_text(json.dumps({"theme": "dark"}))

    ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})

    assert _read(target)["theme"] == "dark"


def test_apply_reports_each_record(target, ledger):
    lines: list[str] = []

    ledger.apply_json(
        Integration.CLAUDE,
        target,
        {"includeGitInstructions": False, "permissions": {"allow": ["Bash(ls)"]}},
        lines.append,
    )

    assert len(lines) == 2
    assert all(line.startswith("  ledger: claude") for line in lines)


def test_apply_writes_backup_once(target, ledger):
    target.write_text(json.dumps({"theme": "dark"}))
    backup = target.with_name(target.name + BACKUP_SUFFIX)

    ledger.apply_json(Integration.CLAUDE, target, {"a": 1})
    ledger.apply_json(Integration.CLAUDE, target, {"b": 2})

    assert _read(backup) == {"theme": "dark"}


def test_rewind_restores_prior_scalar(target, ledger):
    target.write_text(json.dumps({"includeGitInstructions": True}))
    ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target) == {"includeGitInstructions": True}


def test_rewind_removes_scalar_that_was_absent(target, ledger):
    ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert "includeGitInstructions" not in _read(target)


def test_rewind_keeps_scalar_changed_by_user_and_warns(target, ledger):
    ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})
    target.write_text(json.dumps({"includeGitInstructions": True}))
    lines: list[str] = []

    ledger.rewind_json(Integration.CLAUDE, target, lines.append)

    assert _read(target) == {"includeGitInstructions": True}
    assert any("warning" in line for line in lines)


def test_rewind_removes_only_kanon_list_items(target, ledger):
    target.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
    ledger.apply_json(Integration.CLAUDE, target, {"permissions": {"allow": ["Bash(cat)"]}})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target)["permissions"]["allow"] == ["Bash(ls)"]


def test_rewind_keeps_list_item_that_user_already_had(target, ledger):
    target.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
    ledger.apply_json(Integration.CLAUDE, target, {"permissions": {"allow": ["Bash(ls)"]}})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target)["permissions"]["allow"] == ["Bash(ls)"]


def test_rewind_keeps_user_added_list_items(target, ledger):
    ledger.apply_json(Integration.CLAUDE, target, {"permissions": {"allow": ["Bash(cat)"]}})
    data = _read(target)
    data["permissions"]["allow"].append("Bash(rm)")
    target.write_text(json.dumps(data))

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target)["permissions"]["allow"] == ["Bash(rm)"]


def test_rewind_empties_ledger(target, ledger):
    ledger.apply_json(Integration.CLAUDE, target, {"a": 1})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert not ledger.path.exists()


def test_rewind_without_ledger_is_noop(target, ledger):
    target.write_text(json.dumps({"a": 1}))

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target) == {"a": 1}


def test_claim_blob_records_path(tmp_path, ledger):
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "skills" / "plan", "directory")

    assert ledger.has_blob(Integration.CLAUDE, tmp_path / "skills" / "plan")


def test_claim_blob_reports_record(tmp_path, ledger):
    lines: list[str] = []

    ledger.claim_blob(Integration.CLAUDE, tmp_path / "plan", "directory", lines.append)

    assert any("ledger: claude directory" in line for line in lines)


def test_has_blob_false_for_unrecorded_path(tmp_path, ledger):
    (tmp_path / "plan").mkdir()

    assert not ledger.has_blob(Integration.CLAUDE, tmp_path / "plan")


def test_owned_blobs_filters_by_kind(tmp_path, ledger):
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "a", "directory")
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "b", "file")

    assert ledger.owned_blobs(Integration.CLAUDE, "directory") == [tmp_path / "a"]
    assert ledger.owned_blobs(Integration.CLAUDE) == [tmp_path / "a", tmp_path / "b"]


def test_release_blobs_forgets_only_that_kind(tmp_path, ledger):
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "a", "directory")
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "b", "file")

    ledger.release_blobs(Integration.CLAUDE, "directory")

    assert ledger.owned_blobs(Integration.CLAUDE) == [tmp_path / "b"]


def test_release_blobs_empties_ledger(tmp_path, ledger):
    ledger.claim_blob(Integration.CLAUDE, tmp_path / "a", "directory")

    ledger.release_blobs(Integration.CLAUDE)

    assert not ledger.path.exists()


def test_apply_invalid_target_raises(target, ledger):
    target.write_text("{ // comment\n}")

    with pytest.raises(JsonFileError):
        ledger.apply_json(Integration.CLAUDE, target, {"includeGitInstructions": False})


def test_rewind_restores_prior_null_scalar(target, ledger):
    target.write_text(json.dumps({"a": None}))
    ledger.apply_json(Integration.CLAUDE, target, {"a": 1})

    ledger.rewind_json(Integration.CLAUDE, target)

    assert _read(target) == {"a": None}


def test_ledger_survives_reload(target, ledger):
    target.write_text(json.dumps({"a": 1}))
    ledger.apply_json(Integration.CLAUDE, target, {"a": 2, "permissions": {"allow": ["Bash(cat)"]}})

    Ledger.load(ledger.path).rewind_json(Integration.CLAUDE, target)

    assert _read(target) == {"a": 1, "permissions": {"allow": []}}


@pytest.mark.parametrize("content", ["not json", "[]", json.dumps({"claude": {"some/path": []}})])
def test_load_unrecognised_ledger_raises(tmp_path, content):
    path = tmp_path / "ledger.json"
    path.write_text(content)

    with pytest.raises(LedgerFileError):
        Ledger.load(path)
