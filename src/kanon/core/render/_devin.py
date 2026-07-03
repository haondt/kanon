from __future__ import annotations

from dataclasses import dataclass
from typing import override

from kanon.core.config import IntegrationSpecificRule
from kanon.core.render._windsurf import WindsurfKanonRenderer

_RULE_OUTPUT_DIR = ".devin/rules"
_SKILL_OUTPUT_DIR = ".devin/workflows"
_SPECIFIC_RULES = [
    IntegrationSpecificRule(
        path="devin-rules",
        frontmatter={"trigger": "always_on"},
        content="""## Project structure
- CRITICAL: The first action in every conversation is reading @.kanon/STRUCTURE.md. Do not respond to the user, write any files or plan any actions until this is complete.
- When running shell commands, prefer using the bash tool over interactive shell execution for better syntax highlighting in the chat window.
- Run `kanon` commands via blocking `run_command` calls; never background + `command_status`.""",
    )
]

@dataclass
class DevinKanonRenderer(WindsurfKanonRenderer):
    @override
    @classmethod
    def _get_rule_output_dir(cls) -> str:
        return _RULE_OUTPUT_DIR
    @override
    @classmethod
    def _get_skill_output_dir(cls):
        return _SKILL_OUTPUT_DIR
    @override
    @classmethod
    def _get_specific_rules(cls):
        return _SPECIFIC_RULES
