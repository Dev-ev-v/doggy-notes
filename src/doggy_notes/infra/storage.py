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

    def write(self, filename: str, data: dict) -> None:
        file_path = self._resolve(filename)
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def read(self, filename: str) -> dict:
        file_path = self._resolve(filename)
        return json.loads(file_path.read_text(encoding="utf-8"))

    def delete(self, filename: str) -> None:
        file_path = self._resolve(filename)
        if file_path.exists():
            file_path.unlink()

    def list_files(self, pattern: str = "*.json") -> Iterable[Path]:
        return sorted(self.base_dir.glob(pattern))