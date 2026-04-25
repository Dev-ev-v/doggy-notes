import json
from pathlib import Path
from my_notes.src.my_notes.domain.note import Note

class NoteRepository:
    def __init__(self, storage, serializer, base_dir: Path):
        self.storage = storage
        self.serializer = serializer
        self.base_dir = base_dir

    def save(self, note: Note):
        path = self.base_dir / f"{note.name}.json"
        data = self.serializer.to_dict(note)
        self.storage.write(path, data)
        return note

    def list(self):
        files = self.storage.list(self.base_dir, "*.json")
        notes = []
        for f in files:
            raw = self.storage.read(f)
            data = json.loads(raw)
            notes.append(self.serializer.json_to_note(data))
        return notes

    def delete(self, index: int):
        files = self.storage.list(self.base_dir, "*.json")
        if index <= 0 or index > len(files):
            return None
        file = files[index - 1]
        self.storage.delete(file)
        return file