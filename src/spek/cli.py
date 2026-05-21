import click
from spek import __version__
from spek.commands.scaffold import init
from spek.commands.sync import sync
from spek.commands.profile import profile
from spek.commands.local import local
from spek.commands.destroy import destroy


@click.group()
@click.version_option(__version__, prog_name="spek")
def cli():
    """Manage AI-assisted development conventions across projects."""


cli.add_command(init)
cli.add_command(sync)
cli.add_command(profile)
cli.add_command(local)
cli.add_command(destroy)
