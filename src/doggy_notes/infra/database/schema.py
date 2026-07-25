import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 5


def create_schema(db_path: Path) -> None:

    if not db_path.parent.exists():
        raise ValueError(
            f"Parent directory does not exist: {db_path.parent}"
        )

    with sqlite3.connect(db_path) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript("""
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            fingerprint TEXT,
            deleted_at TEXT
        );

        CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE note_tags (
            note_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE UNIQUE INDEX idx_notes_fingerprint ON notes(fingerprint);
        CREATE INDEX idx_tags_name ON tags(name);
        CREATE INDEX idx_note_tags_note_id ON note_tags(note_id);
        CREATE INDEX idx_note_tags_tag_id ON note_tags(tag_id);
        CREATE INDEX idx_notes_title ON notes(title);
        """)

        conn.execute("""
            INSERT INTO metadata(key, value)
            VALUES ('schema_version', ?)
        """, (str(CURRENT_SCHEMA_VERSION),))