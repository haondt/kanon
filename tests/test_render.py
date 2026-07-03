from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import jinja2

from kanon.core.config import Integration, KanonConfig, SourcedResource
from kanon.core.kanons import Kanon
from kanon.core.render import render_kanon, render_settings


@pytest.fixture
def project(tmp_path):
    kanon_dir = tmp_path / ".kanon"
    kanon_dir.mkdir()
    (kanon_dir / "kanon.yaml").write_text(
        yaml.dump(
            {
                "meta": {
                    "kanon_version": "0.0.0",
                    "kanon_sha": "abc",
                    "integrations": ["claude"],
                },
                "kanons": [],
            }
        )
    )
    KanonConfig.initialize(tmp_path)
    return tmp_path


def _render(content: str, ref: str, integration: Integration) -> Path:
    resource = SourcedResource.parse(ref)
    kanon = Kanon.load(content)
    return render_kanon(resource, kanon, integration)


# ── render_settings ───────────────────────────────────────────────────────────


def test_render_settings_always_writes_for_claude(project):
    render_settings(Integration.CLAUDE, [])
    assert (project / ".claude" / "settings.json").exists()


def test_render_settings_writes_hardcoded_hooks(project):
    render_settings(Integration.CLAUDE, [])
    data = json.loads((project / ".claude" / "settings.json").read_text())
    assert data["includeGitInstructions"] is False
    assert "hooks" in data
    assert "SessionStart" in data["hooks"]
    matchers = [e["matcher"] for e in data["hooks"]["SessionStart"]]
    assert "startup" in matchers
    assert "clear" in matchers


def test_render_settings_writes_permissions(project):
    render_settings(Integration.CLAUDE, ["Bash(kanon ref *)", "Skill(my-skill)"])
    data = json.loads((project / ".claude" / "settings.json").read_text())
    assert data["permissions"] == {"allow": ["Bash(kanon ref *)", "Skill(my-skill)"]}


def test_render_settings_accepts_set(project):
    render_settings(Integration.CLAUDE, {"Skill(my-skill)", "Bash(kanon ref *)"})
    data = json.loads((project / ".claude" / "settings.json").read_text())
    assert data["permissions"] == {"allow": ["Bash(kanon ref *)", "Skill(my-skill)"]}


def test_render_settings_windsurf_skips(project):
    render_settings(Integration.WINDSURF, [])
    assert not (project / ".windsurf").exists()


def test_render_settings_devin_skips(project):
    render_settings(Integration.DEVIN, [])
    assert not (project / ".devin").exists()


def test_render_settings_opencode_writes_json(project):
    render_settings(Integration.OPENCODE, [])
    assert (project / "opencode.json").exists()


def test_render_settings_opencode_has_schema_and_instructions(project):
    render_settings(Integration.OPENCODE, [])
    data = json.loads((project / "opencode.json").read_text())
    assert data["$schema"] == "https://opencode.ai/config.json"
    assert ".kanon/STRUCTURE.md" in data["instructions"]
    assert ".opencode/rules/**/*.md" in data["instructions"]
    # STRUCTURE.md should come first so it's loaded before rules
    assert data["instructions"].index(".kanon/STRUCTURE.md") < data[
        "instructions"
    ].index(".opencode/rules/**/*.md")


def test_render_settings_opencode_does_not_write_claude_permissions(project):
    render_settings(Integration.OPENCODE, ["Bash(kanon ref *)"])
    data = json.loads((project / "opencode.json").read_text())
    assert "permissions" not in data


# ── render_kanon: opencode ────────────────────────────────────────────────────


def test_render_kanon_opencode_rule_writes_file(project):
    content = "---\nkanon: {}\n---\nFollow the rule.\n"
    out = _render(content, "test/my-rule", Integration.OPENCODE)
    assert (
        out
        == project / ".opencode" / "rules" / "kanon" / "kanon" / "test" / "my-rule.md"
    )
    assert "Follow the rule." in out.read_text()


def test_render_kanon_opencode_rule_strips_frontmatter(project):
    content = "---\nkanon: {}\n---\nRule body.\n"
    out = _render(content, "test/plain", Integration.OPENCODE)
    assert "---" not in out.read_text()
    assert "Rule body." in out.read_text()


def test_render_kanon_opencode_skill_writes_skill_md(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.OPENCODE)
    assert out == project / ".opencode" / "skills" / "my-skill" / "SKILL.md"
    text = out.read_text()
    assert "name: my-skill" in text
    assert "description: A test skill" in text
    assert "Do the thing." in text


def test_render_kanon_opencode_skill_without_name_raises(project):
    content = "---\nkanon:\n  output: skill\n  description: No name set\n---\nBody.\n"
    with pytest.raises(ValueError, match="kanon.name"):
        _render(content, "workflow/unnamed", Integration.OPENCODE)


# ── render_kanon: codex ──────────────────────────────────────────────────────


def test_render_kanon_codex_rule_writes_agents_managed_block(project):
    content = "---\nkanon: {}\n---\nFollow the rule.\n"
    out = _render(content, "test/my-rule", Integration.CODEX)
    assert out == project / "AGENTS.md"
    text = out.read_text()
    assert "<!-- kanon:codex:start -->" in text
    assert "## test/my-rule" in text
    assert "Follow the rule." in text
    assert "<!-- kanon:codex:end -->" in text


def test_render_kanon_codex_rule_preserves_existing_agents_content(project):
    agents = project / "AGENTS.md"
    agents.write_text("# Project Instructions\n\n- Keep this.\n")

    _render("---\nkanon: {}\n---\nGenerated rule.\n", "test/generated", Integration.CODEX)

    text = agents.read_text()
    assert "# Project Instructions" in text
    assert "- Keep this." in text
    assert "Generated rule." in text


def test_render_kanon_codex_skill_writes_repo_skill(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.CODEX)
    assert out == project / ".agents" / "skills" / "my-skill" / "SKILL.md"
    text = out.read_text()
    assert "name: my-skill" in text
    assert "description: A test skill" in text
    assert "Do the thing." in text


def test_render_kanon_codex_skill_without_name_raises(project):
    content = "---\nkanon:\n  output: skill\n  description: No name set\n---\nBody.\n"
    with pytest.raises(ValueError, match="kanon.name"):
        _render(content, "workflow/unnamed", Integration.CODEX)


# ── render_kanon: rules ──────────────────────────────────────────────────────


def test_render_kanon_rule_writes_file(project):
    content = "---\nkanon: {}\n---\nFollow the rule.\n"
    out = _render(content, "test/my-rule", Integration.CLAUDE)
    assert (
        out == project / ".claude" / "rules" / "kanon" / "kanon" / "test" / "my-rule.md"
    )
    assert "Follow the rule." in out.read_text()


def test_render_kanon_strips_frontmatter_from_rule(project):
    content = "---\nkanon: {}\n---\nRule body.\n"
    out = _render(content, "test/plain", Integration.CLAUDE)
    assert "---" not in out.read_text()
    assert "Rule body." in out.read_text()


def test_render_kanon_windsurf_rule_has_trigger_always_on(project):
    content = "---\nkanon: {}\n---\nThis is a Windsurf rule.\n"
    out = _render(content, "test/windsurf-rule", Integration.WINDSURF)
    text = out.read_text()
    assert "trigger: always_on" in text
    assert "This is a Windsurf rule." in text


def test_render_kanon_devin_rule_has_trigger_always_on(project):
    content = "---\nkanon: {}\n---\nThis is a Devin rule.\n"
    out = _render(content, "test/devin-rule", Integration.DEVIN)
    text = out.read_text()
    assert "trigger: always_on" in text
    assert "This is a Devin rule." in text


def test_render_kanon_devin_skill_writes_workflow(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.DEVIN)
    assert out == project / ".devin" / "workflows" / "my-skill.md"
    text = out.read_text()
    assert "description: A test skill" in text
    assert "Do the thing." in text


# ── render_kanon: skills ─────────────────────────────────────────────────────


def _skill_content(
    model_invokable: bool = True,
    needs_context: bool = True,
    preapproved: list | None = None,
) -> str:
    skill_block = ""
    if not model_invokable or not needs_context:
        parts = []
        if not model_invokable:
            parts.append("    model_invokable: false")
        if not needs_context:
            parts.append("    needs_context: false")
        skill_block = "  skill:\n" + "\n".join(parts) + "\n"
    pre = ""
    if preapproved:
        pre = "  preapproved_tools:\n" + "".join(f"    - {t}\n" for t in preapproved)
    return dedent(f"""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
        {skill_block}{pre}---
        Do the thing.
        """)


def test_render_kanon_skill_writes_skill_md(project):
    content = _skill_content()
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    assert out == project / ".claude" / "skills" / "my-skill" / "SKILL.md"
    assert "Do the thing." in out.read_text()


def test_render_kanon_skill_without_name_raises(project):
    content = "---\nkanon:\n  output: skill\n  description: No name set\n---\nBody.\n"
    with pytest.raises(ValueError, match="kanon.name"):
        _render(content, "workflow/unnamed", Integration.CLAUDE)


def test_render_kanon_fork_skill_appends_preload_command(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
          skill:
            needs_context: false
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    text = out.read_text()
    assert "## Project structure" in text
    assert "Bash(test .kanon/STRUCTURE.md)" in text
    assert "Bash(cat .kanon/STRUCTURE.md)" in text


def test_render_kanon_fork_skill_sets_context_fork(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
          skill:
            needs_context: false
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    text = out.read_text()
    assert "context: fork" in text


def test_render_kanon_skill_model_not_invokable(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
          skill:
            model_invokable: false
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    text = out.read_text()
    assert "disable-model-invocation: true" in text


def test_render_kanon_skill_preapproved_tools_in_frontmatter(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: merge-test
          description: Test merging
          preapproved_tools:
            - Bash(kanon ref *)
          skill:
            needs_context: false
        ---
        Body.
        """)
    out = _render(content, "test/merge-test", Integration.CLAUDE)
    text = out.read_text()
    assert "Bash(kanon ref *)" in text


def test_render_kanon_windsurf_skill_writes_workflow(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: my-skill
          description: A test skill
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.WINDSURF)
    assert out == project / ".windsurf" / "workflows" / "my-skill.md"
    text = out.read_text()
    assert "description: A test skill" in text
    assert "Do the thing." in text


# ── render_kanon: jinja ──────────────────────────────────────────────────────


def _jinja_rule(body: str) -> str:
    return f"---\nkanon:\n  template: jinja\n---\n{body}\n"


def test_render_kanon_jinja_branches_on_kanons(project):
    kanon_dir = project / ".kanon"
    (kanon_dir / "kanon.yaml").write_text(
        yaml.dump(
            {
                "meta": {
                    "kanon_version": "0.0.0",
                    "kanon_sha": "abc",
                    "integrations": ["claude"],
                },
                "kanons": ["python/style"],
            }
        )
    )
    KanonConfig.initialize(project)

    body = "{% if 'python/style' in kanons %}python present{% else %}python absent{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-mod", Integration.CLAUDE)
    assert "python present" in out.read_text()


def test_render_kanon_jinja_absent_kanon(project):
    body = "{% if 'python/style' in kanons %}python present{% else %}python absent{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-mod", Integration.CLAUDE)
    assert "python absent" in out.read_text()


def test_render_kanon_jinja_branches_on_integrations(project):
    body = "{% if 'claude' in integrations %}has claude{% else %}no claude{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-int", Integration.CLAUDE)
    assert "has claude" in out.read_text()


def test_render_kanon_no_template_unaffected(project):
    content = "---\nkanon: {}\n---\nPlain body with {{ literal braces }}.\n"
    out = _render(content, "test/plain", Integration.CLAUDE)
    assert "{{ literal braces }}" in out.read_text()


def test_render_kanon_jinja_absent_arg_is_falsy(project):
    body = "{% if args.missing %}present{% else %}absent{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-args", Integration.CLAUDE)
    assert "absent" in out.read_text()


def test_render_kanon_jinja_branches_on_flag_arg(project):
    body = "{% if args.baz %}baz set{% else %}baz unset{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-args[baz]", Integration.CLAUDE)
    assert "baz set" in out.read_text()


def test_render_kanon_jinja_branches_on_key_value_arg(project):
    body = "{% if args.mode == 'short' %}short mode{% else %}long mode{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-args[mode=short]", Integration.CLAUDE)
    assert "short mode" in out.read_text()


def test_render_kanon_jinja_args_empty_when_none(project):
    body = "{{ args }}"
    out = _render(_jinja_rule(body), "test/jinja-args", Integration.CLAUDE)
    assert out.read_text().strip() == "{}"


def test_render_kanon_jinja_unknown_variable_raises(project):
    body = "{{ undefined_var }}"
    with pytest.raises(jinja2.UndefinedError):
        _render(_jinja_rule(body), "test/jinja-undef", Integration.CLAUDE)


def test_render_kanon_jinja_source_builtin_kanon(project):
    body = "{{ source }}"
    out = _render(_jinja_rule(body), "test/jinja-source", Integration.CLAUDE)
    assert out.read_text().strip() == "kanon::kanon"


def test_render_kanon_jinja_source_alias(project):
    body = "{{ source }}"
    out = _render(_jinja_rule(body), "myalias::test/jinja-source", Integration.CLAUDE)
    assert out.read_text().strip() == "myalias"


def test_render_kanon_jinja_source_external_library(project):
    body = "{{ source }}"
    out = _render(
        _jinja_rule(body), "gh::haondt/kanons::test/jinja-source", Integration.CLAUDE
    )
    assert out.read_text().strip() == "gh::haondt/kanons"


def test_render_kanon_jinja_with_skill_output(project):
    content = dedent("""\
        ---
        kanon:
          output: skill
          name: jinja-skill
          description: A Jinja-templated skill
          template: jinja
        ---
        {% if 'python/style' in kanons %}python present{% else %}python absent{% endif %}
        """)
    out = _render(content, "test/jinja-skill", Integration.CLAUDE)
    assert out == project / ".claude" / "skills" / "jinja-skill" / "SKILL.md"
    assert "python absent" in out.read_text()
