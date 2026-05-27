import click
from spek import __version__
from spek.core.config import SpekConfig
from spek.commands.scaffold import init
from spek.commands.sync import sync
from spek.commands.profile import profile
from spek.commands.local import local
from spek.commands.module import module
from spek.commands.source import source
from spek.commands.check import check
from spek.commands.destroy import destroy
from spek.commands.ref import ref
from spek.commands.session import session
from spek.commands.todo import todo


@click.group()
@click.version_option(__version__, prog_name="spek")
@click.option("--project-root", default=".", type=click.Path(exists=True, file_okay=False))
def cli(project_root: str) -> None:
    """Manage AI-assisted development conventions across projects."""
    SpekConfig.initialize(project_root)


cli.add_command(init)
cli.add_command(sync)
cli.add_command(profile)
cli.add_command(local)
cli.add_command(module)
cli.add_command(source)
cli.add_command(check)
cli.add_command(destroy)
cli.add_command(ref)
cli.add_command(session)
cli.add_command(todo)
