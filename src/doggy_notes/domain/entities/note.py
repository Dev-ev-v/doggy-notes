from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from dataclasses import fields
import hashlib
import uuid

def _generate_id() -> str:
    return uuid.uuid4().hex
    

def _normalize(s: str) -> str:
	return s.strip().lower()


def _build_fingerprint(title: str, content: str) -> str:
    raw = f"{_normalize(title)}|{_normalize(content)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
            

@dataclass
class Note:
    content: str
    title: str
    description: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    fingerprint: str = field(init=False)
    id: str = field(default_factory=_generate_id)

    def __post_init__(self):
        self.fingerprint = _build_fingerprint(self.title, self.content)