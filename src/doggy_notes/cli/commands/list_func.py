import typer
from typing import Optional, List
from doggy_notes.domain.entities.note import Note
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
            tags_list = use_case.execute(tags)
            for name, tag_list in tags_list.items():
            	console.list_notes(name, [presenter.format(tag) for tag in tag_list])
        else:
            notes = use_case.execute()
            console.list_notes("Notes", presenter.format_many(notes))
    except (
        EmptyStorageError
    ) as e:
        console.error(e)