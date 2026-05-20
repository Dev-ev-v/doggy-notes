# storage/mappers.py
from doggy_notes.domain.entities.note import Note
from datetime import datetime

class NoteMapper:
    @staticmethod
    def to_row(note: Note):
        tags = "," + ",".join(
            sorted(set(t.strip().lower() for t in note.tags))
) + ","
        return (
        	note.content,
            note.title,
            note.description,
            tags,
            note.date.isoformat(),
            note.id,
        )

    @staticmethod
    def from_row(row):
        return Note(
            content=row["content"],
            title=row["title"],
            description=row["description"],
            tags = [t.strip().lower() for t in row["tags"].split(",") if t.strip()],
            date=datetime.fromisoformat(row["date"]),
            id=row["id"]
        )