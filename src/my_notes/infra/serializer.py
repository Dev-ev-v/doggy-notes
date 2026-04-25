import json
from datetime import datetime
from my_notes.domain.note import Note


class NoteSerializer:
	def to_dict(self, note: Note):
	       return {
        	"content": note.content,
        	"title": note.title,
        	"description": note.description,
        	"tags": note.tags,
        	"date": note.date.isoformat()
	       }
	
	def json_to_note(self, raw: str):
	    data = json.loads(raw)
	    return Note(
            content=data["content"],
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
            date=datetime.fromisoformat(data["date"])
        )
	
	def note_to_json(self, note: Note) -> str:
	       return json.dumps(self.to_dict(note), ensure_ascii=False, indent=2)