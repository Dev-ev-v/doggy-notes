import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager

from doggy_notes.domain.entities.note import Note
from doggy_notes.domain.repositories.note_repository import NoteRepository
from doggy_notes.infra.persistence.mappers.note_mapper import NoteMapper

from doggy_notes.domain.exceptions.note_errors import NoteAmbiguousIDError

logger = logging.getLogger(__name__)


class SQLiteNoteRepository(NoteRepository):

    def __init__(self, db_path: Path, note_config):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.note_config = note_config

    # -------------------------
    # CREATE
    # -------------------------

    def create(self, note: Note) -> None:
    	with self._transaction("created", note.id):
    		self.conn.execute("""
    			INSERT INTO notes (content, title, description, created_at, updated_at, fingerprint, id)
    			VALUES (?, ?, ?, ?, ?, ?, ?)
    		""", NoteMapper.to_insert_row(note))
    		self._save_tags(note.id, note.tags)


    # -------------------------
    # UPDATE
    # -------------------------

    def update(self, note: Note) -> None:
        with self._transaction("update", note.id):
            self.conn.execute("""
                UPDATE notes
                SET content = ?, title = ?, description = ?, updated_at = ?, fingerprint = ?
                WHERE id = ?
            """, NoteMapper.to_update_row(note))
            
            self.conn.execute("DELETE FROM note_tags WHERE note_id = ?", (note.id,))
            self._save_tags(note.id, note.tags)


    # -------------------------
    # DELETE
    # -------------------------

    def add_to_trash(self, note: Note) -> None:
    	with self._transaction("added to trash", note.id):
    	    self.conn.execute("""
    	        UPDATE notes
    	        SET deleted_at = strftime('%s', 'now')
    	        WHERE id = ?
    	    """, (note.id,))    	
    	    	
    	
    def restore_from_trash(self, note: Note) -> None:
    	with self._transaction("restored from trash", note.id):
    	    self.conn.execute("""
    	        UPDATE notes
    	        SET deleted_at = NULL
    	        WHERE id = ?""", (note.id,))    	    	   
    	        
    
    def delete(self, note: Note) -> None:
        with self._transaction("deleted from storage", note.id):
        	self.conn.execute("""
        	    DELETE FROM notes 
        	    WHERE deleted_at IS NOT NULL
        	    AND id = ?""", (note.id,))
        
        
    # -------------------------
    # READ
    # -------------------------

    def get_by_id(self, note_id: str, trash: bool = False) -> Note | None:
        
        condition = "IS NOT NULL" if trash else "IS NULL"
        location = "trash" if trash else "storage"
        
        logger.debug("Selecting notes by id %s from %s", note_id, location)
        
        cursor = self.conn.execute(f"""
            SELECT * FROM notes 
            WHERE deleted_at {condition}
            AND id = ?
        """, (note_id,))
        row = cursor.fetchone()
        notes_qnt = 1 if row else 0
        
        logger.debug("%d notes found with ID %s", notes_qnt, note_id)

        if not row:
            return None

        note = NoteMapper.from_row(row)
        note.tags = self._load_tags(note.id)
        return note


    def get_by_short_id(self, short_id: str, trash: bool = False) -> Note | None:
        condition = "IS NOT NULL" if trash else "IS NULL"
        location = "trash" if trash else "storage"
        
        logger.debug("Selecting notes by short_id %s from %s", short_id, location)
        
        cursor = self.conn.execute(f"""
            SELECT * FROM notes
            WHERE deleted_at {condition}
            AND substr(id, 1, ?) = ?
        """, (self.note_config.short_id_length, short_id))


        rows = cursor.fetchall()
        notes_qnt = len(rows) if rows else 0
        
        logger.debug("%d notes found with short_id %s", notes_qnt, short_id)

        if len(rows) > 1:
        	raise NoteAmbiguousIDError(short_id, len(rows))

        if not rows:
            return None

        note = NoteMapper.from_row(rows[0])
        note.tags = self._load_tags(note.id)
        return note


    def get_all(self, trash: bool = False) -> list[Note]:
        condition = "IS NOT NULL" if trash else "IS NULL"
        location = "trash" if trash else "storage"
        
        logger.debug("Searching all notes from %s", location)
        
        cursor = self.conn.execute(f"""
            SELECT * FROM notes
            WHERE deleted_at {condition}
            ORDER BY created_at DESC
        """)

        return self._map_rows_with_tags(cursor.fetchall())


    def get_by_tags(self, tags: list[str], mode: str, trash: bool = False) -> list[Note]:
        condition = "IS NOT NULL" if trash else "IS NULL"
        location = "trash" if trash else "storage"
        
        logger.debug("Searching notes by tags %s from %s", tags, location)

        if mode == "AND":
            placeholders = ",".join("?" * len(tags))
            cursor = self.conn.execute(f"""
                SELECT notes.*
                FROM notes
                JOIN note_tags nt
                    ON notes.id = nt.note_id
                JOIN tags t
                    ON t.id = nt.tag_id
                WHERE deleted_at {condition}
                AND t.name IN ({placeholders})
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
                WHERE deleted_at {condition}
                AND t.name IN ({placeholders})
                ORDER BY notes.created_at DESC
            """, (*tags,))
            
        else:
        	raise ValueError(f"Invalid mode, must be 'AND' or 'OR', not {mode}")

        return self._map_rows_with_tags(cursor.fetchall())


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


    def exists_by_fingerprint(self, fingerprint: str) -> str | None:
        row = self.conn.execute(
        	"SELECT id FROM notes WHERE fingerprint = ?",
        	(fingerprint,)).fetchone()
        return row["id"] if row else None
                
    
    def exists_by_id(self, id: str) -> bool:
        row = self.conn.execute(
        	"SELECT 1 FROM notes WHERE id = ?", (id,)).fetchone()
        return row is not None
        
    
    # -------------------------
    # HELPERS
    # -------------------------
    
    @contextmanager
    def _transaction(self, action: str, note_id: str):
    	try:
    		with self.conn:
    			yield    	
    	except sqlite3.Error:
    		logger.exception("Cannot %s note %s", action, note_id)
    		raise
    	
    	logger.debug("Note %s successfully %s", note_id, action)