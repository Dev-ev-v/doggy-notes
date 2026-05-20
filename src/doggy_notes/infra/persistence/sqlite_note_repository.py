from pathlib import Path
import sqlite3

from doggy_notes.domain.entities.note import Note
from doggy_notes.domain.repositories.note_repository import NoteRepository
from doggy_notes.infra.persistence.mappers.note_mapper import NoteMapper
from doggy_notes.cli.parsers.note_parser import NoteParser

class SQLiteNoteRepository(NoteRepository):

    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row

    def create(self, note: Note) -> None:
        self.conn.execute("""
            INSERT INTO notes
            (content, title, description, tags, date, id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, NoteMapper.to_row(note))
        self.conn.commit()

    def update(self, note: Note) -> None:
        self.conn.execute("""
            UPDATE notes
            SET
            	content = ?,
                title = ?,
                description = ?,
                tags = ?,
                date = ?
            WHERE id = ?
        """, NoteMapper.to_row(note))
        self.conn.commit()

    def get_by_id(self, note_id: str) -> Note | None:
        cursor = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()
        return self._map_row(row)

    def get_by_short_id(self, short_id: str) -> Note | None:
        cursor = self.conn.execute(
            "SELECT * FROM notes WHERE substr(id, 1, 8) = ?",
            (short_id,)
        )
        rows = cursor.fetchall()        
        if len(rows) > 1:
            raise ValueError(
                f"Short ID collision: {len(rows)} notes found for '{short_id}'"
            )        
        return self._map_row(rows[0]) if rows else None

    def get_by_tag(self, tag: str) -> list[Note]:
        normalized_tags = NoteParser.parse_tags([tag])        
        if not normalized_tags:
            return []        
        normalized = normalized_tags[0].casefold()        
        cursor = self.conn.execute(
            "SELECT * FROM notes WHERE ',' || tags || ',' LIKE ?",
            (f"%,{normalized},%",)
        )        
        return self._map_rows(cursor.fetchall())

    def get_all(self) -> list[Note]:
        cursor = self.conn.execute(
            "SELECT * FROM notes ORDER BY date DESC"
        )
        return self._map_rows(cursor.fetchall())

    def delete(self, note: Note) -> None:
        self.conn.execute(
            "DELETE FROM notes WHERE id = ?",
            (note.id,)
        )
        self.conn.commit()
        
    def _map_row(self, row) -> Note | None:
        return NoteMapper.from_row(row) if row else None

    def _map_rows(self, rows: list) -> list[Note]:
        return [NoteMapper.from_row(row) for row in rows]

    def close(self):
        self.conn.close()