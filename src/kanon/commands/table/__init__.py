from __future__ import annotations

import click

from kanon.commands.table.commands import (
    table_add,
    table_clear,
    table_edit,
    table_link,
    table_lint,
    table_merge,
    table_remove,
    table_set_status,
    table_status,
    table_unlink,
)


@click.group()
def table() -> None:
    """Track conversation threads as a graph of items."""


table.add_command(table_status)
table.add_command(table_add)
table.add_command(table_edit)
table.add_command(table_set_status)
table.add_command(table_link)
table.add_command(table_unlink)
table.add_command(table_merge)
table.add_command(table_remove)
table.add_command(table_clear)
table.add_command(table_lint)
