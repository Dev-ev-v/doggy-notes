from rich.text import Text

from dataclasses import dataclass
from typing import Optional
from doggy_notes.domain.entities.note import Note
from doggy_notes.presentation.formatters.date_formatter import DateFormatter

@dataclass
class NotePresenterConfig:
    id_style: str = "bold magenta"
    date_style: str = "blue"

class NotePresenter:
    
    @staticmethod
    def separate(width: int=115, color: str="Yellow", format: str="—"):
    	text = Text()
    	text.append("\n" * 2)
    	text.append(format * width, style=color)
    	text.append("\n" * 2)
    	return text
    
    @staticmethod
    def format_detail(note: Note) -> Text:
    	text = Text()
    	text.append("ID: ", style="dim")
    	text.append(note.id, style=NotePresenterConfig.id_style)
    	text.append("\n")
    	text.append("Title: ", style="dim")
    	text.append(note.title or "Untitled")
    	text.append("\n")
    	text.append("Created: ", style="dim")
    	text.append(str(note.date), style=NotePresenterConfig.date_style)
    	text.append("\n")
    	text.append("Tags: ", style="dim")
    	tags = ", ".join(note.tags) if note.tags else "No tags"
    	text.append(tags)
    	text.append("\n" * 2)
    	text.append("Description: ", style="dim")
    	text.append(note.description or "No description")
    	text.append("\n" * 2)
    	text.append("Content: ", style="dim")
    	text.append(note.content)
    	text.append(NotePresenter.separate())
    	return text
    	
    @staticmethod
    def format(note: Note, info: dict = None) -> Text:
    	short_id = note.id[:8]
    	title = note.title or "Untitled"
    	date = DateFormatter.format(str(note.date))
    	text = Text()
    	text.append("[", style="dim")
    	text.append(short_id, style=NotePresenterConfig.id_style)
    	text.append("] ", style="dim")
    	text.append(title)
    	text.append(" (", style="dim")
    	text.append(date, style=NotePresenterConfig.date_style)
    	text.append(")", style="dim")
    	if info:
    		text.append("\n" * 2)
    		for key, i in info.items():
    			text.append(f"{str.capitalize(key)}: ", style="dim")
    			text.append(i)  			
    		text.append(NotePresenter.separate(55))
    	return text
    
    @staticmethod
    def format_many(notes: list[Note]) -> list[Text]:
    	return [NotePresenter.format(note) for note in notes]
    	
class ErrorsPresenter:
	
	@staticmethod
	def format_errors(errors: dict[str, list[str]]) -> Text:
	   text = Text()
	   text.append("\n")
	   for i, (error_key, error_messages) in enumerate(errors.items()):
	       text.append(f"- {error_key}: ", style="dim")
	       text.append(", ".join(error_messages), style="dim")
	       
	       if i < len(errors) - 1:
	       	text.append("\n")
	   return text