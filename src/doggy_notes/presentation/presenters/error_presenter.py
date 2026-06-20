from rich.text import Text
from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
    NoteValidationError,
)

class ErrorPresenter:
	
	@staticmethod
	def format(error) -> Text:
		text = Text()
		match error:
		    case SearchFilterError():
		    	text.append(f"[underline]{error}:[/underline] \n\n")
		    	text.append(f"[bold red]Filter:[/bold red] ")
		    	text.append(f"[green]{error.filter}[/green] \n")
		    	text.append(f"[bold red]Invalid values:[/bold red] ")
		    	if error.value == "ids":
		    		style="id"
		    	elif error.value == "tags":
		    		style="tag"
		    	text.append(f"[{style}]{error.value}[/{style}]")
		    case NoteNotFoundError():
		    	text.append(f"{error.message}\n")
		    	for key, value in error.filters.items():
		    		text.append(f"\n[bold red]{key}:[/bold red] ")
		    		if key == "ids":
		    			style="id"
		    		elif key == "tags":
		    			style="tag"
		    		text.append(f"[{style}]{', '.join(value)}[/{style}]")
		    case NoteEmptyStorageError():
		    	text.append(str(error))
		    case _:
		    	text = error
		return text