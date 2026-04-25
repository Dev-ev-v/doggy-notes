from pathlib import Path
from my_notes.domain.note import Note
from my_notes.infra.serializer import NoteSerializer
from my_notes.infra.storage import NoteStorage

class NoteRepository:
    def __init__(self, storage: NoteStorage, serializer: NoteSerializer, base_dir: Path):
        self.storage = storage
        self.serializer = serializer
        self.base_dir = base_dir

    def save(self, note: Note):
        path = self.base_dir / f"{note.name}.json"
        data = self.serializer.to_dict(note)
        self.storage.write(path, data)
        return note
        
    def get_files(self):
    	return self.storage.list_files(self.base_dir, "*.json")

    def get_notes(self):
        files = self.get_files()
        return [self.serializer.json_to_note(self.storage.read(f)) for f in files]
        
    def get_note(self, indexes: list[int] | None):
        if not indexes:
        	return []
        notes = self.get_notes()
        return [notes[i - 1] for i in indexes if 1 <= i <= len(notes)]
		
    def delete(self, indexes: list[int] | None):
        for i in indexes:
        	self.storage.delete(self.base_dir / f"{i.name}.json")