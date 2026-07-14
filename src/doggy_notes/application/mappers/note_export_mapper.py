from datetime import datetime
from doggy_notes.domain.entities.note import Note


class NoteExportMapper:
	
	@staticmethod
	def to_dict(note: Note) -> dict:
		return {
       	 "id": note.id,
      	  "title": note.title,
     	   "content": note.content,
      	  "description": note.description,
     	   "tags": note.tags,
    	    "created_at": note.created_at.isoformat() if isinstance(note.created_at, datetime) else note.created_at,
     	   "fingerprint": note.fingerprint,
   	 }