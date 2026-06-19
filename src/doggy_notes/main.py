import typer
import logging
try:
    from doggy_notes._version import version as __version__
except ImportError:
    from importlib.metadata import version as _version
    __version__ = _version("doggy-notes")

from pathlib import Path

from doggy_notes.cli.dependencies import get_container

from doggy_notes.cli.commands.create_app import create_app
from doggy_notes.cli.commands.list_app import list_app
from doggy_notes.cli.commands.delete_app import delete_app
from doggy_notes.cli.commands.info_app import info_app
from doggy_notes.cli.commands.edit_app import edit_app
from doggy_notes.cli.commands.read_app import read_app
from doggy_notes.cli.commands.path_app import path_app

from doggy_notes.cli.help_messages import HelpMessages

logging.basicConfig(
    filename=get_container().paths.log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

logger = logging.getLogger(__name__)

context_settings = {
    "help_option_names": ["-h", "--help"]
}

app = typer.Typer(
	help="A simple CLI for managing notes.",
    context_settings=context_settings
)

@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        is_eager=True
    ),
    verbose: bool = typer.Option(
    	False,
    	"--verbose",
    	"-verb",
    	help="Show logs",
    	)
):
    if version:
        typer.echo(f"doggy-notes {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
    else:
    	if verbose:
    		logging.getLogger().setLevel(logging.DEBUG)
    	get_container().initialize_database()
    	
app.add_typer(delete_app, name="delete", help=HelpMessages.DELETE_APP_MESSAGE)

app.add_typer(read_app, name="read", help=HelpMessages.READ_APP_MESSAGE)

app.command(name="create", help=HelpMessages.CREATE_APP_MESSAGE)(create_app)

app.command(name="list", help=HelpMessages.LIST_APP_MESSAGE)(list_app)

app.command(name="info", help=HelpMessages.INFO_APP_MESSAGE)(info_app)

app.command(name="edit")(edit_app)

app.command(name="path", help=HelpMessages.PATH_APP_MESSAGE)(path_app)

if __name__ == "__main__":
    app()