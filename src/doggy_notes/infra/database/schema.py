import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_schema(db_path: Path) -> None:
    if not db_path.parent.exists():
        raise ValueError(f"Parent directory does not exist: {db_path.parent}")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            fingerprint TEXT
        );

        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS tags (
    		id INTEGER PRIMARY KEY AUTOINCREMENT,
  	  	name TEXT UNIQUE NOT NULL
		);

        CREATE TABLE IF NOT EXISTS note_tags (
            note_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
        """)
        
        conn.executescript("""

   		 CREATE INDEX IF NOT EXISTS 						idx_note_tags_note_id
   			 ON note_tags(note_id);

    		CREATE INDEX IF NOT EXISTS 						idx_note_tags_tag_id
 			   ON note_tags(tag_id);
""")

    
def initialize_schema_version(db_path: Path):
    CURRENT_SCHEMA_VERSION = 4
        
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
      	  INSERT OR IGNORE INTO metadata (key, value)
            VALUES ('schema_version', ?)
            """,
            (str(CURRENT_SCHEMA_VERSION),)
    )  
        
    logger.debug(f"Initialized schema_version to {CURRENT_SCHEMA_VERSION}")  
           