import logging
import sqlite3
from pathlib import Path

from doggy_notes.domain.entities.note import build_fingerprint
from doggy_notes.infra.database.schema import CURRENT_SCHEMA_VERSION

logger = logging.getLogger(__name__)


# ============================================================
# Schema Version Helpers
# ============================================================

def get_schema_version(cursor, conn=None) -> int:
    	
    if conn:
    	cursor.executescript("""
    		CREATE TABLE IF NOT EXISTS metadata (
      		  key TEXT PRIMARY KEY,
      	 	 value TEXT
  	 	 );
  	  """)
  	  
    	conn.commit()
    
    try:
        cursor.execute("""
            SELECT value
            FROM metadata
            WHERE key = 'schema_version'
        """)

        row = cursor.fetchone()

        return int(row[0]) if row else 0

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
        	return 0
        raise


def set_schema_version(cursor, version: int) -> None:

    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES ('schema_version', ?)
    """, (str(version),))

# ============================================================
# File Handling
# ============================================================


def backfill_fingerprints(cursor, conn):
    
    cursor.executescript("""
        DELETE FROM notes
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM notes
            GROUP BY
                TRIM(LOWER(COALESCE(title, ''))),
                TRIM(LOWER(COALESCE(content, '')))
        );
    """)
    conn.commit()
    
    rows = cursor.execute(
        "SELECT id, title, content FROM notes WHERE fingerprint IS NULL"
    ).fetchall()

    for row in rows:
        fp = build_fingerprint(row["title"], row["content"])
        cursor.execute(
            "UPDATE notes SET fingerprint = ? WHERE id = ?",
            (fp, row["id"])
        )

    if rows:
        conn.commit()
        logger.debug("Backfilled %d fingerprints", len(rows))
        

# ============================================================
# Migration V0 -> V1
# ============================================================

def migrate_v0_to_v1(
    cursor,
    conn,
):
    logger.debug("Starting V0 -> V1 migration")

    # Changes now are made in database_bootstrap
    
    set_schema_version(cursor, 1)
    
    conn.commit()

    logger.debug("Schema upgraded to V1")


# ============================================================
# Migration V1 -> V2
# ============================================================


def migrate_v1_to_v2(cursor, conn):
    
    cursor.execute("PRAGMA table_info(notes)")
    columns = {row[1] for row in cursor.fetchall()}
    
    if "time" in columns:
        cursor.execute("""
        	ALTER TABLE notes RENAME COLUMN time TO date
 	   """)    

    cursor.execute("""
        UPDATE notes
        SET date = date || '+00:00'
        WHERE date NOT LIKE '%Z'
        AND date NOT GLOB '*[+-][0-9][0-9]:[0-9][0-9]'
    """)

    set_schema_version(cursor, 2)

    conn.commit()

    logger.debug(
        "Schema upgraded to V2"
    )


# ============================================================
# Migration V2 -> V3
# ============================================================

def migrate_v2_to_v3(cursor, conn):

    logger.debug(
        "Starting V2 -> V3 migration"
    )

    logger.info(
        "Migrating tags to relational model"
    )

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS note_tags (
            note_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,

            PRIMARY KEY (note_id, tag_id),

            FOREIGN KEY(note_id)
                REFERENCES notes(id)
                ON DELETE CASCADE,

            FOREIGN KEY(tag_id)
                REFERENCES tags(id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_note_tags_note_id
        ON note_tags(note_id);

        CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id
        ON note_tags(tag_id);
    """)

    cursor.execute("PRAGMA table_info(notes)")
    columns = {row["name"] for row in cursor.fetchall()}

    if "tags" not in columns:

        logger.debug(
            "Legacy collumn 'note.tags' not found.  Nothin to migrate"
        )

        set_schema_version(cursor, 3)
        conn.commit()

        logger.debug(
            "Schema upgraded to V3"
        )

        return

    cursor.execute("""
        SELECT id, tags
        FROM notes
        WHERE tags IS NOT NULL
        AND tags != ''
    """)

    rows = cursor.fetchall()

    migrated_relations = 0

    for row in rows:

        note_id = row["id"]

        raw_tags = row["tags"]

        tags = list(dict.fromkeys([
            tag.strip().lower()
            for tag in raw_tags.split(",")
            if tag.strip()
        ]))

        for tag in tags:

            cursor.execute("""
                INSERT OR IGNORE INTO tags (name)
                VALUES (?)
            """, (tag,))

            cursor.execute("""
                SELECT id
                FROM tags
                WHERE name = ?
            """, (tag,))

            tag_id = cursor.fetchone()["id"]

            cursor.execute("""
                INSERT OR IGNORE INTO note_tags (
                    note_id,
                    tag_id
                )
                VALUES (?, ?)
            """, (note_id, tag_id))

            migrated_relations += 1

    set_schema_version(cursor, 3)

    conn.commit()

    logger.debug(
        "V3 migration completed "
        "(%s relations migrated)",
        migrated_relations
    )

        
# ============================================================
# Migration V3 -> V4
# ============================================================

def migrate_v3_to_v4(cursor, conn):
    logger.debug("Starting V3 -> V4 migration")

    cursor.execute("PRAGMA table_info(notes)")
    columns = {row["name"] for row in cursor.fetchall()}

    if "fingerprint" not in columns:
        logger.debug("Adding missing fingerprint column")
        cursor.execute(
            "ALTER TABLE notes ADD COLUMN fingerprint TEXT"
        )
        
        cursor.execute("""
    	    CREATE UNIQUE INDEX idx_notes_fingerprint
       	 ON notes(fingerprint)
  	  """)
        
    backfill_fingerprints(cursor, conn)

    cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_tags_name
        ON tags(name);
    """)
    
    cursor.execute("""
        ALTER TABLE notes RENAME COLUMN date TO created_at;
    """)    	    
    
    logger.debug("Adding missing updated_at column")
        
    cursor.execute(
        "ALTER TABLE notes ADD COLUMN updated_at TEXT"
    )
        
    cursor.execute("""
        UPDATE notes
  	  SET updated_at = CURRENT_TIMESTAMP
  	  WHERE updated_at IS NULL;
    """)

    set_schema_version(cursor, 4)
    conn.commit()

    logger.debug("V4 migration completed") 
    

# ============================================================
# Migration V4 -> V5
# ============================================================

def migrate_v4_to_v5(cursor, conn):
    logger.debug("Starting V4 -> V5 migration")
    
    cursor.execute("""
    	CREATE INDEX IF NOT EXISTS idx_notes_title
    	ON notes(title);
    """)
    
    cursor.execute("""
        ALTER TABLE notes ADD COLUMN deleted_at TEXT;    
    """)

    set_schema_version(cursor, 5)
    conn.commit()

    logger.debug("V5 migration completed")             


# ============================================================
# Entry Point
# ============================================================

def migrate_database(db_path: Path, max_version: int = CURRENT_SCHEMA_VERSION) -> None:
    
    logger.debug("Starting database migrations")

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        initial_version = get_schema_version(cursor, conn)
        version = initial_version

        if version < 1 and max_version >= 1:
            migrate_v0_to_v1(cursor, conn)
            version = get_schema_version(cursor)

        if version < 2 and max_version >= 2:
            migrate_v1_to_v2(cursor, conn)
            version = get_schema_version(cursor)

        if version < 3 and max_version >= 3:
            migrate_v2_to_v3(cursor, conn)
            version = get_schema_version(cursor)

        if version < 4 and max_version >= 4:
            migrate_v3_to_v4(cursor, conn)
            version = get_schema_version(cursor)

        if version < 5 and max_version >= 5:
            migrate_v4_to_v5(cursor, conn)
            version = get_schema_version(cursor)

        if version == initial_version:
            logger.debug("Schema is up to date (version %d)", version)
        else:
            logger.info("Migrated schema from version %d to %d", initial_version, version)