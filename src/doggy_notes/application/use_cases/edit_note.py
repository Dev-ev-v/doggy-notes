import typer
import logging
from datetime import datetime, timezone

from doggy_notes.domain.entities.note import build_fingerprint
from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)

logger = logging.getLogger(__name__)

class EditNoteUseCase:
	def __init__(self, service, editor):
		self.service = service
		self.editor = editor
		
	
	def open_editor(self, initial_text: str | list) -> str:
		if isinstance(initial_text, list):
			initial_text = ", ".join(initial_text)
		return self.editor.open_editor(initial_text)

	
	def resolve_note(self, id: str):
		result = self.service.get([id])
		note = result.items[0] if result.items else None
		return note
		
	
	def execute(self, note, field: str, text: str):
	   setattr(note, field, text)
	   
	   note.fingerprint = build_fingerprint(note.title, note.content)
	   note.updated_at = datetime.now(timezone.utc)
	   
	   success, error_msg = self.service.update(note)
	   
	   return success, error_msg		  