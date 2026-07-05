import json
import logging
import shutil
import sqlite3
import re
from pathlib import Path

from doggy_notes.application.use_cases.legacy_importer import LegacyImporterUseCase

logger = logging.getLogger(__name__)


# ============================================================
# Schema Version Helpers
# ============================================================

def get_schema_version(cursor) -> int:

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

def archive_file(json_file: Path) -> None:

    archive_dir = json_file.parent / "archived"
    backup_dir = json_file.parent / "backup"

    archive_dir.mkdir(exist_ok=True)
    backup_dir.mkdir(exist_ok=True)

    backup_path = backup_dir / json_file.name
    archived_path = archive_dir / json_file.name

    shutil.copy2(json_file, backup_path)

    shutil.move(
        str(json_file),
        str(archived_path)
    )

    logger.info(
        "Archived legacy file: %s",
        json_file.name
    )


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
        fp = LegacyImporterUseCase._build_fingerprint(row["title"], row["content"])
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
    legacy_dir: Path | None = None
):
    logger.debug("Starting V0 -> V1 migration")

    if legacy_dir is None:
        logger.debug("No legacy directory provided. Skipping JSON import.")
        set_schema_version(cursor, 1)
        conn.commit()
        return

    imported_files = []

    for json_file in legacy_dir.glob("*.json"):
        try:
            ok = LegacyImporterUseCase.import_json_note(cursor, json_file)
            if ok:
                imported_files.append(json_file)
        except Exception:
            logger.exception("Failed to import %s", json_file)

    set_schema_version(cursor, 1)
    conn.commit()

    archive_failed = []

    for json_file in imported_files:
        try:
            archive_file(json_file)
        except Exception:
            logger.exception("Failed to archive %s", json_file)
            archive_failed.append(json_file)

    if archive_failed:
        logger.warning(
            "%d file(s) could not be archived: %s",
            len(archive_failed),
            [f.name for f in archive_failed]
        )

    logger.debug("Schema upgraded to V1")


# ============================================================
# Migration V1 -> V2
# ============================================================

def migrate_v1_to_v2(cursor, conn):

    logger.debug(
        "Normalizing timestamps"
    )

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
            "ALTER TABLE notes ADD COLUMN fingerprint TEXT UNIQUE"
        )
    
    backfill_fingerprints(cursor, conn)

    cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_tags_name
        ON tags(name);
    """)
    
    cursor.executescript("""
        ALTER TABLE notes RENAME COLUMN date TO created_at;
        ALTER TABLE notes ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP;
    """)

    set_schema_version(cursor, 4)
    conn.commit()

    logger.debug("V4 migration completed")  


# ============================================================
# Entry Point
# ============================================================

def migrate_database(
    db_path: Path,
    legacy_dir: Path = None
) -> None:

    logger.debug(
        "Starting database migrations"
    )

    with sqlite3.connect(db_path) as conn:

        conn.row_factory = sqlite3.Row

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = conn.cursor()

        initial_version = get_schema_version(cursor)
        version = initial_version

        if version < 1:

            migrate_v0_to_v1(
                cursor,
                conn,
                legacy_dir
            )

            version = get_schema_version(cursor)

        if version < 2:

            migrate_v1_to_v2(
                cursor,
                conn
            )

            version = get_schema_version(cursor)

        if version < 3:

            migrate_v2_to_v3(
                cursor,
                conn
            )
            
            version = get_schema_version(cursor)
        
        if version < 4:
        	
        	migrate_v3_to_v4(
        		cursor,
        		conn
        	)
        	
        	version = get_schema_version(cursor)

        if version == initial_version:
            logger.debug("Schema is up to date (version %d)", version)
        else:
            logger.info("Migrated schema from version %d to %d", initial_version, version)