import sqlite3
import logging
from pathlib import Path

from doggy_notes.domain.entities.note import Note
from doggy_notes.domain.repositories.note_repository import NoteRepository
from doggy_notes.infra.persistence.mappers.note_mapper import NoteMapper


logger = logging.getLogger(__name__)


class SQLiteNoteRepository(NoteRepository):

    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    # -------------------------
    # Metadata
    # -------------------------

    def get_schema_version(self) -> int:
        cursor = self.conn.execute("""
            SELECT value FROM metadata WHERE key = 'schema_version'
        """)
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, note: Note) -> None:
        logger.debug("Creating note %s", note.id)

        self.conn.execute("""
            INSERT INTO notes (content, title, description, date, id)
            VALUES (?, ?, ?, ?, ?)
        """, NoteMapper.to_row(note))

        self._save_tags(note.id, note.tags)

        self.conn.commit()
        logger.info("Note created: %s", note.id)

    # -------------------------
    # UPDATE
    # -------------------------

    def update(self, note: Note) -> None:
        logger.debug("Updating note %s", note.id)

        self.conn.execute("""
            UPDATE notes
            SET content = ?,
                title = ?,
                description = ?,
                date = ?
            WHERE id = ?
        """, NoteMapper.to_row(note))

        # reset tags (important fix)
        self.conn.execute("""
            DELETE FROM note_tags WHERE note_id = ?
        """, (note.id,))

        self._save_tags(note.id, note.tags)

        self.conn.commit()
        logger.info("Note updated: %s", note.id)

    # -------------------------
    # READ
    # -------------------------

    def get_by_id(self, note_id: str) -> Note | None:
        cursor = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        note = NoteMapper.from_row(row)
        note.tags = self._load_tags(note.id)
        return note

    def get_by_short_id(self, short_id: str) -> Note | None:
        cursor = self.conn.execute("""
            SELECT * FROM notes
            WHERE substr(id, 1, 8) = ?
        """, (short_id,))

        rows = cursor.fetchall()

        if len(rows) > 1:
            raise ValueError(f"Short ID collision: {len(rows)} results")

        if not rows:
            return None

        note = NoteMapper.from_row(rows[0])
        note.tags = self._load_tags(note.id)
        return note

    def get_all(self) -> list[Note]:
        cursor = self.conn.execute("""
            SELECT * FROM notes ORDER BY date DESC
        """)

        return self._map_rows_with_tags(cursor.fetchall())

    def get_by_tags(self, tags: list[str], mode: str) -> list[Note]:
        logger.debug("Searching notes by tags: %s", tags)

        if mode == "AND":
            placeholders = ",".join("?" * len(tags))
            cursor = self.conn.execute(f"""
                SELECT notes.*
                FROM notes
                JOIN note_tags nt
                    ON notes.id = nt.note_id
                JOIN tags t
                    ON t.id = nt.tag_id
                WHERE t.name IN ({placeholders})
                GROUP BY notes.id
                HAVING COUNT(DISTINCT t.name) = ?
            """, (*tags, len(tags)))

        elif mode == "OR":
            placeholders = ",".join("?" * len(tags))
            cursor = self.conn.execute(f"""
                SELECT DISTINCT notes.*
                FROM notes
                JOIN note_tags nt ON notes.id = nt.note_id
                JOIN tags t ON t.id = nt.tag_id
                WHERE t.name IN ({placeholders})
                ORDER BY notes.date DESC
            """, (*tags,))

        return self._map_rows_with_tags(cursor.fetchall())

    # -------------------------
    # DELETE
    # -------------------------

    def delete(self, note: Note) -> None:
    	logger.info("Deleting note %s", note.id)
    	self.conn.execute("DELETE FROM notes WHERE id = ?", (note.id,))
    	self.conn.commit()

    # -------------------------
    # TAG SYSTEM
    # -------------------------

    def _save_tags(self, note_id: str, tags: list[str]) -> None:
        for tag in tags:
            if not tag:
                continue

            self.conn.execute("""
                INSERT OR IGNORE INTO tags (name)
                VALUES (?)
            """, (tag,))

            tag_id = self.conn.execute("""
                SELECT id FROM tags WHERE name = ?
            """, (tag,)).fetchone()[0]

            self.conn.execute("""
                INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                VALUES (?, ?)
            """, (note_id, tag_id))

    def _load_tags(self, note_id: str) -> list[str]:
        cursor = self.conn.execute("""
            SELECT t.name
            FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
        """, (note_id,))

        return [row[0] for row in cursor.fetchall()]

    # -------------------------
    # MAPPING
    # -------------------------

    def _map_rows_with_tags(self, rows) -> list[Note]:
        notes = []

        for row in rows:
            note = NoteMapper.from_row(row)
            note.tags = self._load_tags(note.id)
            notes.append(note)

        return notes

    def close(self):
        self.conn.close()