import typer
from importlib.metadata import version

from doggy_notes.cli.commands.add import app as add_app
from doggy_notes.cli.commands.list_notes import app as list_app
from doggy_notes.cli.commands.delete import app as delete_app
from doggy_notes.cli.commands.info import app as info_app

context_settings = {
    "help_option_names": ["-h", "--help"]
}

app = typer.Typer(
	help="CLI Notes App",
    context_settings=context_settings
)

def version_callback(value: bool):
    if value:
        print(f"doggy-notes {version('doggy-notes')}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def root(
    version_flag: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    )
):
    pass
    
app.add_typer(add_app)
app.add_typer(list_app)
app.add_typer(delete_app)
app.add_typer(info_app)

def main():
    app()

if __name__ == "__main__":
    main()