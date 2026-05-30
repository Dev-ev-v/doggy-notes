import typer
import logging
try:
    from doggy_notes._version import version as __version__
except ImportError:
    from importlib.metadata import version as _version
    __version__ = _version("doggy-notes")

from pathlib import Path

from doggy_notes.cli.dependencies import get_container
from doggy_notes.cli.commands.add import add
from doggy_notes.cli.commands.list_func import list_func
from doggy_notes.cli.commands.delete import delete
from doggy_notes.cli.commands.info import info
from doggy_notes.cli.commands.edit import edit
from doggy_notes.cli.commands.read import read

logging.basicConfig(
    filename=get_container().paths.logs_file,
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
    	

app.command()(add)
app.command(name="list")(list_func)
app.command()(delete)
app.command()(info)
app.command()(edit)
app.command()(read)

if __name__ == "__main__":
    app()