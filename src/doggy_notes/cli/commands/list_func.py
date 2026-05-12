import typer
from typing import Optional, List
from doggy_notes.cli.dependencies import get_service
from doggy_notes.application.use_cases.list_notes import ListNotesUseCase
from doggy_notes.infra.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console
from doggy_notes.domain.exceptions.note_errors import (
    EmptyStorageError
)

def list_func(
    tags: Optional[List[str]] = typer.Argument(None)
):
    service = get_service()
    presenter = NotePresenter()
    console = Console()
    use_case = ListNotesUseCase(service)
    try:
        if tags:
            tags = list(dict.fromkeys(tags))
            tag_filters, notes_groups = use_case.execute(tags)
            for tag, notes in zip(tag_filters, notes_groups):
                console.note(presenter.format_many(notes), tag)
        else:
            notes = use_case.execute()
            for note in notes:
                console.note(presenter.format(note))
    except (
        EmptyStorageError
    ) as e:
        console.error(e)