import logging
from typing import Optional, List
from datetime import datetime, timezone

from doggy_notes.domain.entities.note import Note


logger = logging.getLogger(__name__)

class CreateNoteUseCase:
    def __init__(self, service, editor):
        self.service = service
        self.editor = editor
        
    
    def generate_note(self, data: dict):
        now = datetime.now(timezone.utc)
        data.setdefault("created_at", now)
        data["updated_at"] = now
        
        if not data["content"]:
        	content = self.editor.open_editor()
        	data["content"] = content
        	
                
        note = Note(**data)        
        if note:
        	logger.debug("Note %s created", note.id)
        	
        return note

    
    def execute(
        self,
        note: Note,
    ):
        success, error_msg = self.service.create(note)
        
        return success, error_msg