from doggy_notes.domain.entities.note import Note
import re
from rich.text import Text
from rich.console import Group
from rich.markup import escape

class NotePresenter:
    
    @staticmethod
    def parse_id(raw_input: str) -> str:
    	return re.sub(r'^[\[\]()\s]+|[\[\]()\s]+$', '', raw_input)
    	
    @staticmethod
    def format(note: Note) -> Text:
        short_id = note.id[:8]
        title = note.title or "Untitled"
        if isinstance(note.date, str):
            date = datetime.fromisoformat(note.date)
        else:
            date = note.date
        text = Text()
        text.append("[", style="dim")
        text.append(short_id, style="bold magenta")
        text.append("] ", style="dim")
        text.append(title)
        text.append(
            f" ({date.strftime('%Y-%m-%d')})",
            style="dim"
        )
        return text
    
    @staticmethod
    def format_many(notes):
    	if not notes:
    		return "[dim]No notes found[/dim]"
    	return Group(
        	*[
            	NotePresenter.format(note)
            	for note in notes
       	 ]
  	  )
    
    @staticmethod
    def format_errors(errors: list[str]):
    	text = Text()
    	text.append("\n" * 2)
    	for i, error in enumerate(errors):
    		text.append(f"• {error} ", style="dim")
    		if i < len(errors) - 1:
    			text.append("\n")
    	return text	  