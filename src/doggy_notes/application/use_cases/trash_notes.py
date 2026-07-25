from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError, NoteEmptyStorageError


class TrashNotesUseCase:

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
            trash=True,
        )

        return result


    def restore(
        self,
        notes,
    ):        
        for note in notes:
        	self.service.restore_from_trash(note)
        	
    
    def delete(
        self,
        notes,
    ):        
        for note in notes:
        	self.service.delete(note)                                                