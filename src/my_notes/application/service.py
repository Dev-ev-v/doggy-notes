from my_notes.json.repository import NoteRepository
from my_notes.domain.note import Note

class NoteService:
    def __init__(self, repo: NoteRepository):
        self.repo = repo

    def get_all_notes(self):
        return self.repo.get_notes()
    
    def get_note_by_index(self, indexes: list[int] | None, all: bool):
         if all:
         	return self.get_all_notes()
         return self.repo.get_note(indexes)  
                
    def create_note(self, note: Note):
    	return self.repo.save(note)
    	
    def delete_note(self, indexes: list[int]):
    	return self.repo.delete(indexes)
    