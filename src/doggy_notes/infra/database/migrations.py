import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_schema(db_path: Path) -> None:
    if not db_path.parent.exists():
        raise ValueError(
            f"Parent directory does not exist: {db_path.parent}"
        )

    try:
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    content TEXT NOT NULL,
                    tags TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        logger.info(
            "Database schema created/verified at %s",
            db_path
        )

    except sqlite3.DatabaseError:
        logger.exception(
            "Failed to initialize database schema"
        )
        raise