class NoteError(Exception):
    pass

class NotesNotFoundError(NoteError):
    def __init__(self, filters: str):
        self.filters = filters
        super().__init__(f"No notes found with the applicated filters: {filters}")

class InvalidNoteError(NoteError):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Invalid {field}: {message}")
        
class InvalidSearchError(NoteError):
	def __init__(self, msg: str, filters: str):
		super().__init__(f"{msg}: {filters}")

class EmptyStorageError(NoteError):
    pass