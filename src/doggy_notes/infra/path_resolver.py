from dataclasses import fields
from pathlib import Path

from doggy_notes.domain.exceptions.note_errors import PathNotFoundError


class PathKeyError(Exception):
    def __init__(self, key: str, available: list[str]):
        self.key = key
        self.available = available
        super().__init__(f"{key!r} not found. Available: {', '.join(available)}")


class PathResolver:
    def __init__(self, paths):
        self._field_map = {f.name: Path(getattr(paths, f.name)) for f in fields(paths)}

    def resolve(self, path: str) -> Path:
        parts = Path(path).parts
        root_name = parts[0]
        if root_name not in self._field_map:
            raise PathKeyError(root_name, sorted(self._field_map))
        resolved = self._field_map[root_name].joinpath(*parts[1:])
        if not resolved.exists():
            raise PathNotFoundError(f"Path does not exist: {resolved}")
        return resolved

    def all_dirs(self) -> dict[str, Path]:
        return {k: v for k, v in self._field_map.items() if k.endswith("_dir")}