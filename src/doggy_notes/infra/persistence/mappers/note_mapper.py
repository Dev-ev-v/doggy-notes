from datetime import datetime
from doggy_notes.domain.entities.note import Note

class NoteMapper:
    @staticmethod
    def to_row(note: Note):
        tags = "," + ",".join(
            tag.strip().lower()
            for tag in (note.tags or [])
        ) + ","
        return (
            note.id,
            note.title,
            note.description,
            note.content,
            tags,
            note.date.isoformat()
        )

    @staticmethod
    def from_row(row):
        return Note(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            content=row["content"],
            tags=[
                tag
                for tag in row["tags"].split(",")
                if tag
            ] if row["tags"] else [],
            date=datetime.fromisoformat(row["date"])
        )