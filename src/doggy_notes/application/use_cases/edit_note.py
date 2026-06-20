import typer
import logging

from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)

logger = logging.getLogger(__name__)

class EditNoteUseCase:
	def __init__(self, service):
		self.service = service

	
	def resolve_note(self, id: str):
		result = self.service.get([id])
		note = result.items[0] if result.items else None
		return note
		
	
	def execute(self, note, field: str, text: str):
	   setattr(note, field, text)
	   result = self.service.update(note)		  