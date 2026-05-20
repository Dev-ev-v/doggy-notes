import typer
from typing import Optional, List

from doggy_notes.domain.exceptions.note_errors import (
    InvalidNoteError,
)

from doggy_notes.cli.dependencies import get_service
from doggy_notes.application.use_cases.create_note import CreateNoteUseCase
from doggy_notes.cli.parsers.note_parser import NoteParser
from doggy_notes.presentation.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console

def add(
    content: str = typer.Argument(
        help="Main note content (required)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Note title (max 100 chars)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Aditional note details",
    ),
    tags: List[str] = typer.Option(
        None,
        "--tag",
        help="Repeat option to add multiple tags, useful to filter",
    ),
):
    """
[bold cyan]Create a note and save it in data_dir[/bold cyan]

Store notes quickly with optional metadata.

[bold yellow]EXAMPLES:[/bold yellow]

  Basic:
    doggy add "Remember to buy milk"

  Complete:
    doggy add "API Endpoints" /
     --title "REST Reference" /
     --tag api /
     --tag documentation /
      -d "Quick reference for v2 endpoints"

[bold yellow]OUTPUT:[/bold yellow]
  [bold green][OK] Note successfully created[/bold green]
  [12345678] REST Reference (2026-05-17)        
"""
    parser = NoteParser()
    service = get_service()
    use_case = CreateNoteUseCase(service)
    presenter = NotePresenter()
    console = Console()
    try:
        if not title:
            title = "Untitled"
        if tags:
       	 tags = parser.parse_tags(tags)
        note = use_case.execute(content=content, title=title, description=description, tags=tags)
        console.success("Note successfully created")
        console.note(presenter.format(note))
    except InvalidNoteError as e:
        console.error(e)