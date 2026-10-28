from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from kanon.cli import cli
from kanon.core.config import KanonConfig, SourceReference, SourcedResource
from kanon.core.sources import SourceResolver

RULE_BODY = "Write concise commit messages."
SKILL = (
    "---\nkanon:\n  output: skill\n  name: kanon-plan\n  description: plan\n---\nPlan it.\n"
)


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    fake = tmp_path / "home"
    fake.mkdir()
    monkeypatch.setenv("HOME", str(fake))
    return fake


def _global_dot_kanon(home: Path) -> Path:
    return home / ".kanon" / "global-project" / ".kanon"


def make_global(home: Path, integrations: list[str] | None = None) -> None:
    dot_kanon = _global_dot_kanon(home)
    kanons = dot_kanon / "kanons" / "kanon" / "kanon"
    (kanons / "git").mkdir(parents=True)
    (kanons / "git" / "commit.md").write_text(RULE_BODY)
    (kanons / "plan.md").write_text(SKILL)
    (dot_kanon / "stances").mkdir()
    (dot_kanon / "kanon.yaml").write_text(
        yaml.dump(
            {
                "meta": {
                    "kanon_version": "0.0.0",
                    "kanon_sha": "abc1234",
                    "integrations": integrations or ["claude"],
                },
                "kanons": ["git/commit", "plan"],
            }
        )
    )


def run(*args: str):
    return CliRunner().invoke(cli, list(args))


def test_global_and_project_root_are_mutually_exclusive(home, tmp_path):
    result = run("-g", "--project-root", str(tmp_path), "list")

    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_global_flag_roots_config_under_global_project(home):
    run("-g", "list")

    assert KanonConfig.root() == _global_dot_kanon(home)
    assert KanonConfig.is_global()


def test_global_sync_writes_rule_under_home_claude_rules(home):
    make_global(home)

    result = run("-g", "sync")

    assert result.exit_code == 0, result.output
    rule = home / ".claude" / "rules" / "kanon" / "kanon" / "kanon" / "git" / "commit.md"
    assert rule.read_text() == RULE_BODY


def test_global_sync_writes_plain_skill_directory(home):
    make_global(home)

    run("-g", "sync")

    skill = (home / ".claude" / "skills" / "kanon-plan" / "SKILL.md").read_text()
    assert "name: kanon-plan" in skill


def test_global_sync_omits_structure_injection_in_skills(home):
    make_global(home)
    (_global_dot_kanon(home) / "kanons" / "kanon" / "kanon" / "plan.md").write_text(
        SKILL.replace("  description: plan", "  description: plan\n  skill:\n    needs_context: false")
    )

    run("-g", "sync")

    skill = (home / ".claude" / "skills" / "kanon-plan" / "SKILL.md").read_text()
    assert "STRUCTURE.md" not in skill
    assert "context: fork" in skill


def test_global_sync_settings_have_no_session_start_hook(home):
    make_global(home)

    run("-g", "sync")

    settings = json.loads((home / ".claude" / "settings.json").read_text())
    assert settings["includeGitInstructions"] is False
    assert "hooks" not in settings


def test_global_sync_does_not_write_into_global_project_dir(home):
    make_global(home)

    run("-g", "sync")

    assert not (home / ".kanon" / "global-project" / ".claude").exists()


def test_global_sync_preserves_user_settings(home):
    make_global(home)
    (home / ".claude").mkdir()
    (home / ".claude" / "settings.json").write_text(json.dumps({"theme": "dark"}))

    run("-g", "sync")

    settings = json.loads((home / ".claude" / "settings.json").read_text())
    assert settings["theme"] == "dark"


def test_global_sync_twice_does_not_duplicate_list_entries(home):
    make_global(home)
    kanon_file = _global_dot_kanon(home) / "kanons" / "kanon" / "kanon" / "git" / "commit.md"
    kanon_file.write_text("---\nkanon:\n  preapproved_tools: ['Bash(ls)']\n---\nbody\n")

    run("-g", "sync")
    run("-g", "sync")

    settings = json.loads((home / ".claude" / "settings.json").read_text())
    assert settings["permissions"]["allow"] == ["Bash(ls)"]


def test_global_sync_leaves_foreign_claude_files(home):
    make_global(home)
    foreign_rule = home / ".claude" / "rules" / "mine.md"
    foreign_skill = home / ".claude" / "skills" / "mine" / "SKILL.md"
    foreign_rule.parent.mkdir(parents=True)
    foreign_skill.parent.mkdir(parents=True)
    foreign_rule.write_text("mine")
    foreign_skill.write_text("mine")

    run("-g", "sync")
    run("-g", "destroy", "--yes")

    assert foreign_rule.exists()
    assert foreign_skill.exists()


@pytest.mark.parametrize("integration", ["codex", "windsurf", "devin", "opencode"])
def test_global_sync_unsupported_integration_errors(home, integration):
    make_global(home, [integration])

    result = run("-g", "sync")

    assert result.exit_code == 1
    assert "Global mode is not supported" in result.output
    assert not (home / ".claude").exists()


def test_global_destroy_removes_kanon_output_and_rewinds_settings(home):
    make_global(home)
    (home / ".claude").mkdir()
    (home / ".claude" / "settings.json").write_text(json.dumps({"theme": "dark"}))
    run("-g", "sync")

    result = run("-g", "destroy", "--yes")

    assert result.exit_code == 0, result.output
    assert not (home / ".claude" / "rules" / "kanon").exists()
    assert not (home / ".claude" / "skills" / "kanon--kanon-plan").exists()
    assert json.loads((home / ".claude" / "settings.json").read_text()) == {"theme": "dark"}
    assert not _global_dot_kanon(home).exists()


def test_global_destroy_keeps_global_settings_and_sources(home):
    make_global(home)
    settings = home / ".kanon" / "settings.yaml"
    sources = home / ".kanon" / "sources" / "x"
    sources.mkdir(parents=True)
    settings.write_text("sources: {}\n")

    run("-g", "destroy", "--yes")

    assert settings.exists()
    assert sources.exists()


def test_global_init_offers_only_supported_integrations(home, monkeypatch):
    seen: dict[str, list] = {}

    class FakeQuestion:
        def __init__(self, value):
            self.value = value

        def ask(self):
            return self.value

    def fake_checkbox(message, choices, **kwargs):
        seen[message] = list(choices)
        return FakeQuestion([c for c in choices] if message == "Select integrations:" else [])

    monkeypatch.setattr("kanon.commands.scaffold.questionary.checkbox", fake_checkbox)
    monkeypatch.setattr("kanon.commands.scaffold.questionary.select", lambda *a, **k: FakeQuestion("none"))

    result = run("-g", "init")

    assert result.exit_code == 0, result.output
    assert [str(i) for i in seen["Select integrations:"]] == ["claude"]
    assert (_global_dot_kanon(home) / "kanon.yaml").exists()


def test_global_source_resolves_in_project_mode(home, tmp_path):
    project = tmp_path / "proj"
    (project / ".kanon").mkdir(parents=True)
    (project / ".kanon" / "kanon.yaml").write_text(
        yaml.dump({"meta": {"kanon_version": "0", "kanon_sha": "a", "integrations": ["claude"]}})
    )
    glob_kanons = _global_dot_kanon(home) / "project" / "kanons"
    glob_kanons.mkdir(parents=True)
    (glob_kanons / "mine.md").write_text("hi")

    run("--project-root", str(project), "list")

    source = SourceResolver.instance()[SourceReference.GLOBAL_SOURCE_REFERENCE]
    assert source.list_kanons() == ["mine"]


def test_global_prefix_expands_to_global_source():
    resource = SourcedResource.parse("global::mine")

    assert resource.source == SourceReference.GLOBAL_SOURCE_REFERENCE


def test_global_source_resolves_when_project_has_no_config(home, tmp_path):
    run("--project-root", str(tmp_path), "list")

    assert SourceReference.GLOBAL_SOURCE_REFERENCE in dict(SourceResolver.instance().items())


def test_global_source_and_project_source_coincide_in_global_mode(home):
    make_global(home)
    local = _global_dot_kanon(home) / "project" / "kanons"
    local.mkdir(parents=True)
    (local / "mine.md").write_text("hi")

    run("-g", "list")

    sources = SourceResolver.instance()
    assert sources[SourceReference.GLOBAL_SOURCE_REFERENCE].list_kanons() == ["mine"]
    assert sources[SourceReference.PROJECT_SOURCE_REFERENCE].list_kanons() == ["mine"]


def test_global_source_rejected_as_source_key():
    with pytest.raises(ValueError):
        SourceReference.parse("kanon::global", validate_as_key=True)


def test_global_sync_prefixes_skill_when_foreign_skill_holds_name(home):
    make_global(home)
    foreign = home / ".claude" / "skills" / "kanon-plan" / "SKILL.md"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("mine")

    run("-g", "sync")

    assert foreign.read_text() == "mine"
    assert "name: kanon-plan" in (home / ".claude" / "skills" / "kanon--kanon-plan" / "SKILL.md").read_text()


def test_global_sync_twice_keeps_plain_skill_directory(home):
    make_global(home)

    run("-g", "sync")
    run("-g", "sync")

    assert (home / ".claude" / "skills" / "kanon-plan" / "SKILL.md").exists()
    assert not (home / ".claude" / "skills" / "kanon--kanon-plan").exists()


def test_global_destroy_keeps_user_skill_with_kanon_prefix(home):
    make_global(home)
    mine = home / ".claude" / "skills" / "kanon--mine" / "SKILL.md"
    mine.parent.mkdir(parents=True)
    mine.write_text("mine")

    run("-g", "sync")
    run("-g", "destroy", "--yes")

    assert mine.exists()


def test_global_destroy_removes_tracked_skill_directory(home):
    make_global(home)

    run("-g", "sync")
    run("-g", "destroy", "--yes")

    assert not (home / ".claude" / "skills" / "kanon-plan").exists()


def test_global_sync_invalid_settings_aborts_without_removing_output(home):
    make_global(home)
    run("-g", "sync")
    settings = home / ".claude" / "settings.json"
    settings.write_text("{ // comment\n}")

    result = run("-g", "sync")

    assert result.exit_code != 0
    assert "not valid JSON" in result.output
    assert (home / ".claude" / "skills" / "kanon-plan" / "SKILL.md").exists()


def test_global_destroy_invalid_settings_aborts_without_removing_config(home):
    make_global(home)
    run("-g", "sync")
    (home / ".claude" / "settings.json").write_text("{ // comment\n}")

    result = run("-g", "destroy", "--yes")

    assert result.exit_code != 0
    assert _global_dot_kanon(home).exists()
