from datetime import datetime
from doggy_notes.domain.entities.note import Note


class NoteMapper:
    @staticmethod
    def to_row(note: Note):
        return (
            note.content,
            note.title,
            note.description,
            note.date.isoformat() if isinstance(note.date, datetime) else note.date,
            note.id,
        )

    @staticmethod
    def from_row(row) -> Note:
        return Note(
            content=row["content"],
            title=row["title"],
            description=row["description"],
            tags=[],
            date=datetime.fromisoformat(row["date"]),
            id=row["id"]
        )