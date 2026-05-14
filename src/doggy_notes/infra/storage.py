from pathlib import Path
import json
from typing import Iterable

APP_NAME = "doggy-notes"

CONFIG_DIR = Path.home() / ".config" / APP_NAME
DATA_DIR = Path.home() / ".local" / "share" / APP_NAME / "sqlite_repo.py"
CACHE_DIR = Path.home() / ".cache" / APP_NAME

for d in (CONFIG_DIR, DATA_DIR, CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)

class NoteStorage:
    def __init__(self, base_dir: Path = DATA_DIR):
        self.base_dir = base_dir

    def resolve(self, filename: str) -> Path:
        return self.base_dir / filename