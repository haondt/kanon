from __future__ import annotations

from typing import Any, override

import click
from kanon import __version__
from kanon.core.config import KanonConfig, KanonEnv
from kanon.core.errors import KanonError
from kanon.core.sources import initialize as sources_initialize
from kanon.commands.scaffold import init
from kanon.commands.sync import sync
from kanon.commands.profile import profile
from kanon.commands.local import local
from kanon.commands.kanons import add, edit, list_cmd, remove, search, set_cmd
from kanon.commands.source import source
from kanon.commands.cache import cache
from kanon.commands.check import check
from kanon.commands.destroy import destroy
from kanon.commands.ref import ref
from kanon.commands.session import session
from kanon.commands.todo import todo
from kanon.commands.table import table


class _KanonGroup(click.Group):
    @override
    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except KanonError as e:
            raise click.ClickException(str(e)) from e


@click.group(cls=_KanonGroup)
@click.version_option(__version__, prog_name="kanon")
@click.option("--project-root", default=None, type=click.Path(exists=True, file_okay=False))
@click.option("-g", "--global", "is_global", is_flag=True,
              help="Operate on the user-level global project (~/.kanon/global-project) instead of a project.")
def cli(project_root: str | None, is_global: bool) -> None:
    """Manage AI-assisted development conventions across projects."""
    if is_global:
        if project_root is not None:
            raise click.UsageError("--global and --project-root are mutually exclusive.")
        KanonConfig.initialize(KanonEnv.instance().global_project_path, is_global=True)
    else:
        KanonConfig.initialize(project_root or ".")
    sources_initialize()


cli.add_command(init)
cli.add_command(sync)
cli.add_command(profile)
cli.add_command(local)
cli.add_command(add)
cli.add_command(edit)
cli.add_command(list_cmd, name="list")
cli.add_command(remove)
cli.add_command(search)
cli.add_command(set_cmd, name="set")
cli.add_command(source)
cli.add_command(cache)
cli.add_command(check)
cli.add_command(destroy)
cli.add_command(ref)
cli.add_command(session)
cli.add_command(todo)
cli.add_command(table)
