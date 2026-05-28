from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import jinja2

from spek.core.config import Integration, SpekConfig, SourcedResource
from spek.core.modules import Module
from spek.core.render import render_module, render_settings


@pytest.fixture
def project(tmp_path):
    spek_dir = tmp_path / ".spek"
    spek_dir.mkdir()
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc", "integrations": ["claude"]},
        "modules": [],
    }))
    SpekConfig.initialize(tmp_path)
    return tmp_path


def _render(content: str, ref: str, integration: Integration) -> Path:
    resource = SourcedResource.parse(ref)
    module = Module.load(content)
    return render_module(resource, module, integration)


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
    render_settings(Integration.CLAUDE, ["Bash(spek ref *)", "Skill(my-skill)"])
    data = json.loads((project / ".claude" / "settings.json").read_text())
    assert data["permissions"] == {"allow": ["Bash(spek ref *)", "Skill(my-skill)"]}


def test_render_settings_accepts_set(project):
    render_settings(Integration.CLAUDE, {"Skill(my-skill)", "Bash(spek ref *)"})
    data = json.loads((project / ".claude" / "settings.json").read_text())
    assert data["permissions"] == {"allow": ["Bash(spek ref *)", "Skill(my-skill)"]}


def test_render_settings_windsurf_skips(project):
    render_settings(Integration.WINDSURF, [])
    assert not (project / ".windsurf").exists()


# ── render_module: rules ──────────────────────────────────────────────────────


def test_render_module_rule_writes_file(project):
    content = "---\nspek: {}\n---\nFollow the rule.\n"
    out = _render(content, "test/my-rule", Integration.CLAUDE)
    assert out == project / ".claude" / "rules" / "spek" / "spek" / "test" / "my-rule.md"
    assert "Follow the rule." in out.read_text()


def test_render_module_strips_frontmatter_from_rule(project):
    content = "---\nspek: {}\n---\nRule body.\n"
    out = _render(content, "test/plain", Integration.CLAUDE)
    assert "---" not in out.read_text()
    assert "Rule body." in out.read_text()


def test_render_module_windsurf_rule_has_trigger_always_on(project):
    content = "---\nspek: {}\n---\nThis is a Windsurf rule.\n"
    out = _render(content, "test/windsurf-rule", Integration.WINDSURF)
    text = out.read_text()
    assert "trigger: always_on" in text
    assert "This is a Windsurf rule." in text



# ── render_module: skills ─────────────────────────────────────────────────────


def _skill_content(model_invokable: bool = True, needs_context: bool = True, preapproved: list | None = None) -> str:
    skill_block = ""
    if not model_invokable or not needs_context:
        parts = []
        if not model_invokable:
            parts.append("    model_invokable: false")
        if not needs_context:
            parts.append("    needs_context: false")
        skill_block = "  skill:\n" + "\n".join(parts) + "\n"
    top_needs = "  needs_context: false\n" if not needs_context else ""
    pre = ""
    if preapproved:
        pre = "  preapproved_tools:\n" + "".join(f"    - {t}\n" for t in preapproved)
    return dedent(f"""\
        ---
        spek:
          output: skill
          name: my-skill
          description: A test skill
        {skill_block}{top_needs}{pre}---
        Do the thing.
        """)


def test_render_module_skill_writes_skill_md(project):
    content = _skill_content()
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    assert out == project / ".claude" / "skills" / "my-skill" / "SKILL.md"
    assert "Do the thing." in out.read_text()


def test_render_module_skill_without_name_raises(project):
    content = "---\nspek:\n  output: skill\n  description: No name set\n---\nBody.\n"
    with pytest.raises(ValueError, match="spek.name"):
        _render(content, "workflow/unnamed", Integration.CLAUDE)


def test_render_module_fork_skill_appends_preload_command(project):
    content = dedent("""\
        ---
        spek:
          output: skill
          name: my-skill
          description: A test skill
          needs_context: false
          skill:
            needs_context: false
        ---
        Do the thing.
        """)
    out = _render(content, "workflow/my-skill", Integration.CLAUDE)
    text = out.read_text()
    assert "## Project structure" in text
    assert "Bash(test .spek/STRUCTURE.md)" in text
    assert "Bash(cat .spek/STRUCTURE.md)" in text


def test_render_module_fork_skill_sets_context_fork(project):
    content = dedent("""\
        ---
        spek:
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


def test_render_module_skill_model_not_invokable(project):
    content = dedent("""\
        ---
        spek:
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


def test_render_module_skill_preapproved_tools_in_frontmatter(project):
    content = dedent("""\
        ---
        spek:
          output: skill
          name: merge-test
          description: Test merging
          preapproved_tools:
            - Bash(spek ref *)
          skill:
            needs_context: false
        ---
        Body.
        """)
    out = _render(content, "test/merge-test", Integration.CLAUDE)
    text = out.read_text()
    assert "Bash(spek ref *)" in text


def test_render_module_windsurf_skill_writes_workflow(project):
    content = dedent("""\
        ---
        spek:
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


# ── render_module: jinja ──────────────────────────────────────────────────────


def _jinja_rule(body: str) -> str:
    return f"---\nspek:\n  template: jinja\n---\n{body}\n"


def test_render_module_jinja_branches_on_modules(project):
    spek_dir = project / ".spek"
    (spek_dir / "spek.yaml").write_text(yaml.dump({
        "meta": {"spek_version": "0.0.0", "spek_sha": "abc", "integrations": ["claude"]},
        "modules": ["python/style"],
    }))
    SpekConfig.initialize(project)

    body = "{% if 'python/style' in modules %}python present{% else %}python absent{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-mod", Integration.CLAUDE)
    assert "python present" in out.read_text()


def test_render_module_jinja_absent_module(project):
    body = "{% if 'python/style' in modules %}python present{% else %}python absent{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-mod", Integration.CLAUDE)
    assert "python absent" in out.read_text()


def test_render_module_jinja_branches_on_integrations(project):
    body = "{% if 'claude' in integrations %}has claude{% else %}no claude{% endif %}"
    out = _render(_jinja_rule(body), "test/jinja-int", Integration.CLAUDE)
    assert "has claude" in out.read_text()


def test_render_module_no_template_unaffected(project):
    content = "---\nspek: {}\n---\nPlain body with {{ literal braces }}.\n"
    out = _render(content, "test/plain", Integration.CLAUDE)
    assert "{{ literal braces }}" in out.read_text()


def test_render_module_jinja_unknown_variable_raises(project):
    body = "{{ undefined_var }}"
    with pytest.raises(jinja2.UndefinedError):
        _render(_jinja_rule(body), "test/jinja-undef", Integration.CLAUDE)


def test_render_module_jinja_with_skill_output(project):
    content = dedent("""\
        ---
        spek:
          output: skill
          name: jinja-skill
          description: A Jinja-templated skill
          template: jinja
        ---
        {% if 'python/style' in modules %}python present{% else %}python absent{% endif %}
        """)
    out = _render(content, "test/jinja-skill", Integration.CLAUDE)
    assert out == project / ".claude" / "skills" / "jinja-skill" / "SKILL.md"
    assert "python absent" in out.read_text()
