from logging.handlers import RotatingFileHandler
from pathlib import Path

from doggy_notes.infra.paths import build_paths

Paths = build_paths()
log_file = Paths.log_file

handler = RotatingFileHandler(
    log_file,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
)