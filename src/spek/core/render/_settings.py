from __future__ import annotations

from typing import Any

from spek.core.config import AI_TOOL_SETTINGS_FILES, PROJECT_SPEK_DIR, Integration, SpekConfig
from spek.core.yaml_utils import save_json
from spek.core.utils import deep_merge

AI_TOOL_ADDITIONAL_SETTINGS: dict[Integration, dict[str, Any]] = {
    Integration.CLAUDE: {
        "includeGitInstructions": False,
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup",
                    "hooks": [{ "type": "command", "command": f"bash -c 'test -f {PROJECT_SPEK_DIR}/STRUCTURE.md && cat {PROJECT_SPEK_DIR}/STRUCTURE.md'" }]
                },
                {
                    "matcher": "clear",
                    "hooks": [{ "type": "command", "command": f"bash -c 'test -f {PROJECT_SPEK_DIR}/STRUCTURE.md && cat {PROJECT_SPEK_DIR}/STRUCTURE.md'" }]
                }
            ]
        }
    }
}

def render_settings(
    integration: Integration,
    preapproved_tools: list[str] | set[str],
) -> None:
    rel = AI_TOOL_SETTINGS_FILES.get(integration)
    if rel is None:
        return
    settings_path = SpekConfig.project_root() / rel
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    tools = sorted(preapproved_tools) if isinstance(preapproved_tools, set) else preapproved_tools
    settings_object: dict[str, Any] = {}
    if tools:
        settings_object["permissions"] = {"allow": tools}
    additional = AI_TOOL_ADDITIONAL_SETTINGS.get(integration)
    if additional:
        settings_object = deep_merge(additional, settings_object)
    save_json(settings_object, settings_path)
