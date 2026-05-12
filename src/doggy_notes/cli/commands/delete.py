import typer
from doggy_notes.application.use_cases.delete_notes import DeleteNotesUseCase
from doggy_notes.cli.dependencies import get_service
from doggy_notes.infra.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console
from doggy_notes.domain.exceptions.note_errors import (
    InvalidNoteSelectionError,
    NoteNotFoundError
)

def delete(
    note_ids: list[str] = typer.Option(None, "--id"),
    delete_all: bool = typer.Option(False, "--all")
    ):
    """Delete a note from data_dir by id or short_id
    """
    service = get_service()
    use_case = DeleteNotesUseCase(service)
    presenter = NotePresenter()
    console = Console()
    try:
        if note_ids:
        	note_ids = [presenter.parse_id(id) for id in note_ids]
        	note_ids = list(dict.fromkeys(note_ids))
        notes, errors = use_case.resolve_notes(
            ids=note_ids,
            delete_all=delete_all,
        )
        if errors:
            console.error(presenter.format_errors(errors))
        for note in notes:
        	console.note(presenter.format(note))
        confirmed = console.confirm("Delete these notes?")
        if not confirmed:
            console.error("Operation cancelled")
            return
        use_case.execute(notes)
        console.success("Notes deleted")
    except (
        typer.BadParameter,
        NoteNotFoundError
    ) as e:
        console.error(str(e))