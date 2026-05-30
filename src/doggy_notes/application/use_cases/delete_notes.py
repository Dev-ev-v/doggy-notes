from doggy_notes.presentation.presenters.note_presenter import (
    NotePresenter,
    ErrorsPresenter,
)

from doggy_notes.cli.console import Console

from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError, NoteEmptyStorageError


class DeleteNotesUseCase:

    def __init__(self, service):
        self.service = service

    def resolve_notes(
        self,
        ids: list[str] | None = None,
        tags: list[str] | None = None,
        delete_all: bool = False,
        mode: str = "AND",
    ):
        result = self.service.get(
            ids=ids,
            tags=tags,
            mode=mode,
        )

        if result.is_empty:
            if tags or ids:
            	filters = {}
            	if tags:
            		filters["tags"] = tags 
            	if ids:
            		filters["ids"] = ids 
            	raise NoteNotFoundError(
            			filters=ErrorsPresenter.format_errors(filters),
            			message="No notes found with the applied filters"
            	)
            raise NoteEmptyStorageError("Empty storage, create a note first")

        return result

    def get_confirmation(
        self,
        result,
    ):
        console = Console()

        quantity = len(result.items)

        confirmed = console.confirm(
            f"{quantity} notes will be deleted. Continue?"
        )

        return confirmed

    def execute(
        self,
        result,
    ):
        deleted = []

        seen_ids = set()

        for note in result.items:

            if note.id in seen_ids:
                continue

            self.service.delete(note)

            seen_ids.add(note.id)

            deleted.append(note)

        return deleted