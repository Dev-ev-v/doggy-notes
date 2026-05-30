import typer
import logging

from doggy_notes.cli.parsers.note_parser import NoteParser

from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)

from doggy_notes.presentation.presenters.note_presenter import (
    ErrorsPresenter,
)

logger = logging.getLogger(__name__)

class EditNoteUseCase:
	def __init__(self, service):
		self.service = service

	def resolve_note(self, id: str):
		result = self.service.get([id])
		note = result.items[0] if result.items else None
		if not note:
			filters = {}
			filters["id"] = [id]
			raise NoteNotFoundError(ErrorsPresenter.format_errors(filters))
		return note
		
	def execute(self, note, field: str, text: str):
	   parser = NoteParser()
	   if field == "tags":
	       tags = [tag.strip() for tag in text.split(',')]
	       print(tags)
	       parsed = parser.parse_tags(tags)
	   else:
	   	parsed = text
	   setattr(note, field, parsed)
	   result = self.service.update(note)		
	   logger.info(f"note_tags: {note.tags}")
	   logger.info(result)