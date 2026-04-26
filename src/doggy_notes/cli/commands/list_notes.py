import typer

from doggy_notes.cli.dependencies import (
    get_service,
    get_printer
)

app = typer.Typer()


@app.command(name="list", help="List all saved notes.")
def list_notes():
    service = get_service()
    printer = get_printer()

    notes = service.get_all_notes()
    printer.print_notes(notes)