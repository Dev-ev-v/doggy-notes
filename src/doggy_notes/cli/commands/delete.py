import typer

from typing import Optional, List

from doggy_notes.cli.dependencies import (
    get_service,
    get_printer
)

app = typer.Typer()


@app.command(help="Delete a note or more.")
def delete(
    index: Optional[List[int]] = typer.Argument(None),
    all: bool = typer.Option(False, "--all")
):
    if all and index:
        raise typer.BadParameter(
            "Use indexes or --all, not both."
        )

    service = get_service()
    printer = get_printer()

    files = service.get_note_by_index(index, all)

    can_delete = printer.get_confirmation(files)

    if can_delete:
        service.delete_note(files)