from pathlib import Path
import sqlite3

from doggy_notes.domain.entities.note import Note
from doggy_notes.domain.repositories.note_repository import NoteRepository
from doggy_notes.infra.persistence.mappers.note_mapper import NoteMapper


class SQLiteNoteRepository(NoteRepository):

    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row

    def save(self, note: Note) -> None:
        self.conn.execute("""
            INSERT INTO notes
            (id, title, description, content, tags, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, NoteMapper.to_row(note))
        self.conn.commit()

    def get_by_id(self, note_id: str) -> Note | None:
        cursor = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()
        return NoteMapper.from_row(row) if row else None
        
    def get_by_short_id(self, short_id: str) -> Note | None:
    	cursor = self.conn.execute(
    	"SELECT * FROM notes WHERE substr(id, 1, 8) = ?",
    	(short_id,)
    	)
    	rows = cursor.fetchall()
    	if len(rows) > 1:
        	raise ValueError("Short ID collision")
    	if not rows:
    		return None
    	return NoteMapper.from_row(rows[0])
        
    def get_by_tag(self, tag: str) -> list[Note]:
    	normalized = tag.strip().lower()
    	cursor = self.conn.execute(
        	"SELECT * FROM notes WHERE tags LIKE ?",
        	(f"%,{normalized},%",)
    	)
    	return [
        	NoteMapper.from_row(row)
        	for row in cursor.fetchall()
    	]

    def get_all(self) -> list[Note]:
        cursor = self.conn.execute(
            "SELECT * FROM notes ORDER BY date DESC"
        )

        return [
            NoteMapper.from_row(row)
            for row in cursor.fetchall()
        ]

    def delete(self, note: Note) -> None:
        self.conn.execute(
            "DELETE FROM notes WHERE id = ?",
            (note.id,)
        )

        self.conn.commit()

    def close(self):
        self.conn.close()