import click
from kanon import __version__
from kanon.core.config import KanonConfig
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


@click.group()
@click.version_option(__version__, prog_name="kanon")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
def cli(project_root: str) -> None:
    """Manage AI-assisted development conventions across projects."""
    KanonConfig.initialize(project_root)
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
