from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Note:
    content: str
    title: str
    description: str
    tags: List[str]
    date: datetime
    
    @property
    def name(self) -> str:
    	return self.title or self.date