from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)


class ReadNotesUseCase:

    
    def __init__(self, service):
        self.service = service

    
    def resolve_notes(
        self,
        ids: list[str] | None = None,
        tags: list[str] | None = None,
        mode="AND",
    ):

        result = self.service.get(ids=ids, tags=tags, mode=mode)

        return result