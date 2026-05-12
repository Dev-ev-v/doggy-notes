import typer
from doggy_notes.domain.repositories.note_repository import NoteRepository
from doggy_notes.domain.exceptions.note_errors import (
    InvalidNoteSelectionError,
    NoteNotFoundError
)

class DeleteNotesUseCase:
    def __init__(self, service):
        self.service = service
        
    def resolve_notes(
        self,
        ids: list[str] | None = None,
        delete_all: bool = False,
    ):
        selectors = [ids is not None, delete_all]
        if sum(selectors) != 1:
            if not sum(selectors):
            	raise typer.BadParameter(
            	"Please use a valid argument")
            else:	
            	raise typer.BadParameter(
                "Choose exactly one delete target."
            	)
        errors = []
        if delete_all:
            notes = self.service.get_service()
        else: 
        	notes = []
        	for note_id in ids:
           	 note = self.service.get_service(note_id)
           	 if note is None:
             	   errors.append(note_id + " don't exist in storage")
           	 else:
            		notes.append(note)
        if not notes:
            raise NoteNotFoundError("Note ids not found in storage")
        return notes, errors

    def execute(
        self,
        notes
    ):
        for note in notes:
            self.service.delete_service(note)
        return notes