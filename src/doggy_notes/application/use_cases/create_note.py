from typing import Optional, List
from datetime import datetime

from doggy_notes.domain.entities.note import Note

class CreateNoteUseCase:
    def __init__(self, service):
        self.service = service

    def execute(
        self,
        content: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: List[str] = None,
    ):
        note = Note(
            content=content,
            title=title,
            description=description,
            tags=tags or [],
            date=datetime.now(),
        )

        self.service.create(note)
        return note