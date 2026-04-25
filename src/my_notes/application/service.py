from my_notes.src.my_notes.json.repository import NoteRepository
from my_notes.src.my_notes.domain.note import Note

class NoteService:
    def __init__(self, repo: NoteRepository):
        self.repo = repo

    def get_all_notes(self):
        return self.repo.list()
        
    def create_note(self, note: Note):
    	return self.repo.save(note)
    	
    def delete_note(index: int):
    	return self.repo.delete(index)
    