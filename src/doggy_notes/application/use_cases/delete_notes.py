from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError, NoteEmptyStorageError


class DeleteNotesUseCase:

    def __init__(self, service):
        self.service = service

    def resolve_notes(
        self,
        ids: list[str] | None = None,
        tags: list[str] | None = None,
        mode: str = "AND",
    ):
        result = self.service.get(
            ids=ids,
            tags=tags,
            mode=mode,
        )

        return result


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