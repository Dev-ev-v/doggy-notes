import logging
from pathlib import Path

from doggy_notes.infra.database.schema import create_schema
from doggy_notes.infra.database.migrations import migrate_database
from doggy_notes.cli.dependencies import get_dependencies


logger = logging.getLogger(__name__)


def initialize_database(db_path: Path):
    logger.debug("Initializing database at %s", db_path)

    if not db_path.exists():

        create_schema(db_path)

        logger.debug("Created new database")

        return

    migrate_database(db_path)
    
    logger.debug("Importing legacy notes")
    
    deps = get_dependencies()
    deps.legacy_importer.import_notes_from_old_dirs()