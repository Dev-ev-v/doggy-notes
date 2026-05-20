import typer
from doggy_notes.cli.parsers.note_parser import NoteParser
from doggy_notes.domain.exceptions.note_errors import (
	NotesNotFoundError,
)
from doggy_notes.presentation.presenters.note_presenter import (
    ErrorsPresenter,
)

class EditNoteUseCase:
	def __init__(self, service):
		self.service = service

	def resolve_note(self, id: str):
		result = self.service.get([id])
		note = result.items[0] if result.items else None
		if not note:
			filters = {}
			filters["id"] = [id]
			raise NotesNotFoundError(ErrorsPresenter.format_errors(filters))
		return note
		
	def execute(self, note, field: str, text: str):
	   parser = NoteParser()
	   if field == "tags":
	       tags = text.splitlines()
	       parsed = parser.parse_tags(tags)
	   else:
	   	parsed = text
	   setattr(note, field, parsed)
	   self.service.update(note)		