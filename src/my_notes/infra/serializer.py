from my_notes.src.my_notes.domain.note import Note

class NoteSerializer:
	def to_dict(self, note: Note):
	       return {
        	"content": note.content,
        	"title": note.title,
        	"description": note.description,
        	"tags": note.tags,
        	"date": note.date.isoformat()
	       }
	
	def json_to_note(self, data: dict):
	    data = json.loads(path.read_text())
	    return Note(
            content=data["content"],
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
            date=datetime.fromisoformat(data["date"])
        )
	
	def note_to_json(self, note: Note) -> str:
	       return json.dumps(self.to_dict(note), ensure_ascii=False, indent=2)
	
	def create_note(self, note: Note) -> Note:
	    file = self.base_dir / f"{note.name}.json"
	    file.write_text(self.note_to_json(note), encoding="utf-8")
	    return note