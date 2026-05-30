import hashlib
import json
import logging
import shutil
import sqlite3
import uuid
import re

from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_DATE_FORMATS = (
    "%Y-%m-%d_%H-%M-%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
)


# ============================================================
# Utils
# ============================================================

def normalize(text: str) -> str:
    text = text or ""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def build_fingerprint(title: str, content: str) -> str:
    """
    Fingerprint version 1:
    title + content
    """

    raw = f"{normalize(title)}|{normalize(content)}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


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

    except sqlite3.DatabaseError:
        return 0


def set_schema_version(cursor, version: int) -> None:

    cursor.execute("""
        INSERT OR REPLACE INTO metadata (key, value)
        VALUES ('schema_version', ?)
    """, (str(version),))


# ============================================================
# Date Parsing
# ============================================================

def parse_timestamp(value: str) -> str:

    if not value:
        raise ValueError("Empty timestamp")

    try:
        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.isoformat()

    except ValueError:
        pass

    for fmt in SUPPORTED_DATE_FORMATS:

        try:
            dt = datetime.strptime(value, fmt)
            dt = dt.replace(tzinfo=timezone.utc)

            return dt.isoformat()

        except ValueError:
            continue

    raise ValueError(
        f"Unsupported timestamp format: {value}"
    )


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


# ============================================================
# JSON Import
# ============================================================

def import_json_note(cursor, json_file: Path) -> bool:

    logger.info(
        "Importing legacy note: %s",
        json_file.name
    )

    data = json.loads(
        json_file.read_text(encoding="utf-8")
    )

    title = data.get("title") or "Untitled"

    content = data.get("content", "")

    note_date = (
        data.get("date")
        or data.get("time")
        or ""
    )

    timestamp = parse_timestamp(note_date)

    fingerprint = build_fingerprint(
        title,
        content
    )

    note_id = uuid.uuid4().hex

    # --------------------------------------------------------
    # Insert note
    # --------------------------------------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO notes (
            id,
            title,
            description,
            content,
            date,
            fingerprint
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        note_id,
        title,
        data.get("description", ""),
        content,
        timestamp,
        fingerprint,
    ))

    if cursor.rowcount == 0:

        logger.info(
            "Skipping duplicate note: %s",
            json_file.name
        )

        return False

    # --------------------------------------------------------
    # Tags migration
    # --------------------------------------------------------

    tags = data.get("tags", [])

    normalized_tags = sorted({
        tag.strip().lower()
        for tag in tags
        if tag.strip()
    })

    for tag in normalized_tags:

        cursor.execute("""
            INSERT OR IGNORE INTO tags (name)
            VALUES (?)
        """, (tag,))

        cursor.execute("""
            SELECT id
            FROM tags
            WHERE name = ?
        """, (tag,))

        tag_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT OR IGNORE INTO note_tags (
                note_id,
                tag_id
            )
            VALUES (?, ?)
        """, (note_id, tag_id))

    logger.info(
        "Imported note successfully: %s",
        json_file.name
    )

    return True


# ============================================================
# Migration V0 -> V1
# ============================================================

def migrate_v0_to_v1(
    cursor,
    conn,
    legacy_dir: Path | None = None
):

    logger.info(
        "Starting V0 -> V1 migration"
    )

    if legacy_dir is None:

        logger.info(
            "No legacy directory provided. "
            "Skipping JSON import."
        )

        set_schema_version(cursor, 1)
        conn.commit()

        return

    imported_files = []

    for json_file in legacy_dir.glob("*.json"):

        try:

            ok = import_json_note(
                cursor,
                json_file
            )

            if ok:
                imported_files.append(json_file)

        except Exception:

            logger.exception(
                "Failed to import %s",
                json_file
            )

    conn.commit()

    for json_file in imported_files:

        try:
            archive_file(json_file)

        except Exception:

            logger.exception(
                "Failed to archive %s",
                json_file
            )

    set_schema_version(cursor, 1)

    conn.commit()

    logger.info(
        "Schema upgraded to V1"
    )


# ============================================================
# Migration V1 -> V2
# ============================================================

def migrate_v1_to_v2(cursor, conn):

    logger.info(
        "Normalizing timestamps"
    )

    cursor.execute("""
        UPDATE notes
        SET date = date || '+00:00'
        WHERE date NOT LIKE '%+%'
        AND date NOT LIKE '%Z'
    """)

    set_schema_version(cursor, 2)

    conn.commit()

    logger.info(
        "Schema upgraded to V2"
    )


# ============================================================
# Migration V2 -> V3
# ============================================================

def migrate_v2_to_v3(cursor, conn):

    logger.info(
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

        CREATE INDEX IF NOT EXISTS idx_tags_name
        ON tags(name);

        CREATE INDEX IF NOT EXISTS idx_note_tags_note_id
        ON note_tags(note_id);

        CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id
        ON note_tags(tag_id);
    """)

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

    logger.info(
        "V3 migration completed "
        "(%s relations migrated)",
        migrated_relations
    )


# ============================================================
# Entry Point
# ============================================================

def migrate_database(
    db_path: Path,
    legacy_dir: Path | None = None
) -> None:

    logger.info(
        "Starting database migrations"
    )

    with sqlite3.connect(db_path) as conn:

        conn.row_factory = sqlite3.Row

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = conn.cursor()

        version = get_schema_version(cursor)

        logger.info(
            "Current schema version: %d",
            version
        )

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

        logger.info(
            "Database migrations completed"
        )