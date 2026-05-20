import click
from spek import __version__
from spek.commands.scaffold import scaffold
from spek.commands.sync import sync
from spek.commands.profile import profile
from spek.commands.local import local


@click.group()
@click.version_option(__version__, prog_name="spek")
def cli():
    """Manage AI-assisted development conventions across projects."""


cli.add_command(scaffold)
cli.add_command(sync)
cli.add_command(profile)
cli.add_command(local)
