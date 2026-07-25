import shutil
import logging
from platformdirs import user_data_dir, user_cache_dir
from pathlib import Path


logger = logging.getLogger(__name__)

APP_NAME = "doggy-notes"

data_dir = Path(user_data_dir(APP_NAME))

cache_dir = Path(user_cache_dir(APP_NAME))

STATIC_NO_FUNCTIONAL_PATHS = [
    data_dir / "exports",
]

LEGACY_DB_DIR = Path.home() / ".local" / "share" / "doggy-notes" / "sqlite_repo.py"


def _log_files():
    return list(cache_dir.glob("*.logs")) + list(cache_dir.glob("*.txt"))


def clean_no_functional_paths(legacy_merge_succeeded: bool = True):

    paths = list(STATIC_NO_FUNCTIONAL_PATHS) + _log_files()

    if legacy_merge_succeeded:
        paths.append(LEGACY_DB_DIR)

    for path in paths:
        if not path.exists():
            continue

        logger.info("Deleting no functional path %s", path)

        if path.is_dir():
            for child in path.iterdir():
                logger.debug("%s from %s is being deleted", child, path)
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()

        logger.debug("%s successfully deleted", path)