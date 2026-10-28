from __future__ import annotations

import click

from kanon.commands.session.commands import session_start, session_goal, session_status, session_lint, session_clear
from kanon.commands.session.plan import session_plan
from kanon.commands.session.amend import session_amend
from kanon.commands.session.build import session_build
from kanon.commands.session.detour import session_detour
from kanon.commands.session.stance import session_stance
from kanon.commands.session.review import session_review


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
