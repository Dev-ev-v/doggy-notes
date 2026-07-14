import logging
import dataclasses
from typing import Optional, List
from datetime import datetime, timezone

from doggy_notes.domain.entities.note import Note
from doggy_notes.domain.exceptions.note_errors import NoteValidationError


logger = logging.getLogger(__name__)

class CreateNoteUseCase:
    def __init__(self, service, editor):
        self.service = service
        self.editor = editor                          
    
    
    def valid_data(self, data: dict, auto: bool = False):
        if not data.get("content"):
        	if not auto:
        		data["content"] = self.editor.open_editor()
        		if not data.get("content"):
        			raise NoteValidationError("content", "Note with empty content")
        	else:
        		data["content"] = "No content"
        
        
    def generate_note(self, data: dict):
        now = datetime.now(timezone.utc)
        data.setdefault("created_at", now)
        data["updated_at"] = now
        	                
        valid_fields = {f.name for f in dataclasses.fields(Note)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}        
        note = Note(**filtered_data)        
        
        if note:
        	logger.debug("Note %s created", note.id)
        	
        return note

    
    def execute(
        self,
        note: Note,
    ):
        		
        success, error_messages = self.service.create(note)
        
        return success, error_messages