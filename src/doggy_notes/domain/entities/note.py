from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from dataclasses import fields
import uuid

def generate_id() -> str:
    return uuid.uuid4().hex

@dataclass
class Note:
    content: str
    title: str
    description: str
    tags: List[str]
    date: datetime
    id: str = field(default_factory=generate_id)