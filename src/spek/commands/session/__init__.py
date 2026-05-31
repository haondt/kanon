from __future__ import annotations

import click

from .commands import session_start, session_goal, session_status, session_lint, session_clear, session_load
from .plan import session_plan
from .amend import session_amend
from .build import session_build
from .detour import session_detour
from .stance import session_stance
from .review import session_review
from .freeze import session_freeze


@click.group()
def session() -> None:
    """Manage the current session."""


session.add_command(session_start)
session.add_command(session_goal)
session.add_command(session_status)
session.add_command(session_lint)
session.add_command(session_clear)
session.add_command(session_plan)
session.add_command(session_amend)
session.add_command(session_build)
session.add_command(session_detour)
session.add_command(session_stance)
session.add_command(session_review)
session.add_command(session_freeze)
session.add_command(session_load)
