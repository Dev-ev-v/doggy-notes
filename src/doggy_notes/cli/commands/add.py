import typer
from typing import Optional, List

from doggy_notes.domain.exceptions.note_errors import (
    InvalidNoteCreateError
)

from doggy_notes.cli.dependencies import get_service
from doggy_notes.application.use_cases.create_note import CreateNoteUseCase
from doggy_notes.infra.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console

def add(
    content: str,
    title: Optional[str] = typer.Option(None, "--title"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    tags: Optional[List[str]] = typer.Option(None, "--tags")
):
    """Create a note and save it in data_dir.  Use `doggy add -h` for more information
    """
    service = get_service()
    use_case = CreateNoteUseCase(service)
    presenter = NotePresenter()
    console = Console()
    try:
    	note = use_case.execute(content=content, title=title, description=description, tags=tags)
    	console.success("Note successfully created")
    	console.note(presenter.format(note))
    except InvalidNoteCreateError as e:
    	console.write(console.error(str(e)))
    	