from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import hashlib
import uuid


def generate_id() -> str:
    return uuid.uuid4().hex


def _normalize(s: str) -> str:
    return s.strip().lower()


def build_fingerprint(title: str, content: str) -> str:
    raw = f"{_normalize(title)}|{_normalize(content)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class Note:
    content: str
    title: str = "Untitled"
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    fingerprint: str = field(init=False)
    id: str = field(default_factory=generate_id)

    def __post_init__(self):
        self.fingerprint = build_fingerprint(self.title, self.content)