import click
from spek import __version__
from spek.commands.scaffold import init
from spek.commands.sync import sync
from spek.commands.profile import profile
from spek.commands.local import local
from spek.commands.module import module
from spek.commands.destroy import destroy
from spek.commands.ref import ref
from spek.commands.session import session
from spek.commands.todo import todo
from spek.commands.plan import plan
from spek.commands.split import split


@click.group()
@click.version_option(__version__, prog_name="spek")
def cli():
    """Manage AI-assisted development conventions across projects."""


cli.add_command(init)
cli.add_command(sync)
cli.add_command(profile)
cli.add_command(local)
cli.add_command(module)
cli.add_command(destroy)
cli.add_command(ref)
cli.add_command(session)
cli.add_command(todo)
cli.add_command(plan)
cli.add_command(split)
