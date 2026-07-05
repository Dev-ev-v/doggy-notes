from datetime import datetime
from doggy_notes.domain.entities.note import Note


class NoteMapper:
    @staticmethod
    def to_insert_row(note: Note):
        return (
       	 note.content,
      	  note.title,
       	 note.description,
       	 note.created_at.isoformat() if isinstance(note.created_at, datetime) else note.created_at,
       	 note.updated_at.isoformat(),
       	 note.fingerprint,
       	 note.id,)
    
    
    @staticmethod
    def to_update_row(note: Note):
        return (
      	  note.content,
       	 note.title,
        	note.description,
       	 note.updated_at.isoformat(),
     	   note.fingerprint,
      	  note.id,
    	)

    
    @staticmethod
    def from_row(row) -> Note:
        return Note(
            content=row["content"],
            title=row["title"],
            description=row["description"],
            tags=[],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            id=row["id"],
        )