class NoteError(Exception):
    pass

class NoteNotFoundError(NoteError):
    pass
    
class InvalidNoteCreateError(NoteError):
	pass

class EmptyStorageError(NoteError):
	pass		