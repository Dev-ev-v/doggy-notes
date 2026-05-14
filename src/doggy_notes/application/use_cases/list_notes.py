from doggy_notes.domain.exceptions.note_errors import (
    EmptyStorageError
)

class ListNotesUseCase:
	def __init__(self, service):
		self.service = service
		
	def execute(self, tags=None):
		notes_list = self.service.get_service(tags=tags)	
		if not notes_list:
			raise EmptyStorageError("No notes in storage, create a note first")
		return notes_list