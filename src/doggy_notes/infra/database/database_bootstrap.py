import logging
from pathlib import Path

from doggy_notes.infra.database.schema import ensure_schema, initialize_schema_version
from doggy_notes.infra.database.migrations import migrate_database


logger = logging.getLogger(__name__)

def initialize_database(db_path: Path):
    db_exists = db_path.exists()

    logger.debug("Initializing database at %s", db_path)

    try:
        ensure_schema(db_path)
    except Exception:
        logger.exception("Failed to initialize database schema at %s", db_path)
        raise

    if not db_exists:
        logger.info("New database created at %s", db_path)
        initialize_schema_version(db_path)
        return

    migrate_database(db_path)