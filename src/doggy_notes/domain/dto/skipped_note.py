from dataclasses import dataclass
from typing import Optional

@dataclass
class SkippedNoteData:
    preview: str
    short_id: str
    date: Optional[str]
    errors: list[str]