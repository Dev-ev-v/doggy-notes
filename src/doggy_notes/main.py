import typer
import logging
try:
    from doggy_notes._version import version as __version__
except ImportError:
    from importlib.metadata import version as _version
    __version__ = _version("doggy-notes")

from pathlib import Path

from doggy_notes.cli.dependencies import get_container
from doggy_notes.infra.database.database_bootstrap import initialize_database
from doggy_notes.infra.database.paths_migrations import clean_no_functional_paths

from doggy_notes.cli.commands.create_app import create_app
from doggy_notes.cli.commands.list_app import list_app
from doggy_notes.cli.commands.delete_app import delete_app
from doggy_notes.cli.commands.info_app import info_app
from doggy_notes.cli.commands.edit_app import edit_app
from doggy_notes.cli.commands.read_app import read_app
from doggy_notes.cli.commands.path_app import path_app
from doggy_notes.cli.commands.import_app import import_app
from doggy_notes.cli.commands.export_app import export_app

from doggy_notes.cli.help_messages import HelpMessages


def setup_logging(verbose: bool = False, log_file: Path = None):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S"
        ))
        root_logger.addHandler(file_handler)

    
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
        root_logger.addHandler(console_handler)
        

logger = logging.getLogger(__name__)

context_settings = {
    "help_option_names": ["-h", "--help"]
}

app = typer.Typer(
	help="A simple CLI for managing notes.",
    context_settings=context_settings
)

container = get_container()


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v",
                                  help="Show version and exit.", is_eager=True),
    verbose: bool = typer.Option(False, "--verbose", "-verb", help="Show logs")
):
    setup_logging(verbose=verbose, log_file=container.paths.log_file)

    if version:
        typer.echo(f"doggy-notes {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
    else:
        initialize_database(container.paths.database_file)
        clean_no_functional_paths()
    	
app.add_typer(delete_app, name="delete", help=HelpMessages.DELETE_APP_MESSAGE)

app.add_typer(read_app, name="read", help=HelpMessages.READ_APP_MESSAGE)

app.add_typer(export_app, name="export", help=HelpMessages.EXPORT_APP_MESSAGE)

app.command(name="create", help=HelpMessages.CREATE_APP_MESSAGE)(create_app)

app.command(name="list", help=HelpMessages.LIST_APP_MESSAGE)(list_app)

app.command(name="info", help=HelpMessages.INFO_APP_MESSAGE)(info_app)

app.command(name="edit", help=HelpMessages.EDIT_APP_MESSAGE)(edit_app)

app.command(name="path", help=HelpMessages.PATH_APP_MESSAGE)(path_app)

app.command(name="import", help=HelpMessages.IMPORT_APP_MESSAGE)(import_app)

if __name__ == "__main__":
    app()