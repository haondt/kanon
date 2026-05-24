from __future__ import annotations

import click

from .commands import todo_status, todo_search, todo_add, todo_remove, todo_lint
from .section import todo_section


@click.group()
def todo() -> None:
    """Manage the project backlog."""


todo.add_command(todo_status)
todo.add_command(todo_search)
todo.add_command(todo_add)
todo.add_command(todo_remove)
todo.add_command(todo_lint)
todo.add_command(todo_section)
