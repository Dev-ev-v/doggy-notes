import typer
from typing import Optional, List
from doggy_notes.domain.entities.note import Note
from doggy_notes.cli.dependencies import get_service
from doggy_notes.cli.parsers.note_parser import NoteParser
from doggy_notes.cli.console import Console
from doggy_notes.presentation.presenters.note_presenter import ErrorsPresenter
from doggy_notes.application.use_cases.read_note import ReadNoteUseCase
from doggy_notes.domain.exceptions.note_errors import (
    NotesNotFoundError,
    InvalidNoteError,
    EmptyStorageError,
)

def read(
    note_ids: Optional[List[str]] = typer.Option(
        None,
        "--id",
        help="Note ID(s) to delete (repeat option for multiple)",
    ),
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        help="Read all notes with these tags (repeat option for multiple)",
    ),
    fields: list[str] = typer.Option(
    	None,
        "--field",
        "-f",
        help="Field to display: 'content', 'title', 'description', or 'tags'",
    ),
    entire: bool = typer.Option(
    	False,
    	"--entire",
    	help="Display all fields (title, description, content, and tags)",
    ),
):
    """
[bold cyan]Display specific fields from a note or all its contents. Display all noted by default[/bold cyan]

Read notes data without editing. Shows formatted output with metadata
and content clearly separated. 

[bold yellow]EXAMPLES:[/bold yellow]

  Read note content (default):
    doggy read
    doggy read --id 12345678
    doggy read --id 12345678 --field content

  Read multiple fields:
    doggy read --field tags
    doggy read --id 12345678 --field title --field tags
    doggy read --id 12345678 --field title --field description --field tags --field content

  Read all note information:
    doggy read --id 12345678 --entire

  Read notes by tags:
    doggy read --tag work --field title --field tags
    doggy read --tag activities --tag important --tag tomorrow --field description --field content
    
  Read multiple notes by ids:
    doggy read --id 12345678 --id 23456789 --entire

[bold yellow]FIELDS:[/bold yellow]

  [bold]content[/bold]      Main note text
  [bold]title[/bold]        Note title
  [bold]description[/bold]  Additional details
  [bold]tags[/bold]         Associated tags

[bold yellow]OUTPUT:[/bold yellow]

  [bold cyan]Single field:[/bold cyan]
    [12345678] REST Reference (2026-05-17)
    
    Content: API Endpoints documentation for v2 integration...

  [bold cyan]All fields (--entire):[/bold cyan]
    [bold]ID:[/bold]          12345678
    [bold]Title:[/bold]       REST Reference
    [bold]Created:[/bold]     2026-05-17
    [bold]Tags:[/bold]       api, documentation
    
    [bold]Description:[/bold]
    Quick reference for v2 endpoints
    
    [bold]Content:[/bold]
    API Endpoints documentation for v2 integration...
"""
    service = get_service()
    parser = NoteParser()
    console = Console()
    use_case = ReadNoteUseCase(service)
    try:
        if note_ids:
       	 note_ids = [parser.parse_id(id) for id in note_ids]
       	 note_ids = list(dict.fromkeys(note_ids))
        if tags:
        	tags = parser.parse_tags(tags)       
        if fields and entire:
       	 raise InvalidNoteError("filter", "Use fields OR entire, not both")
        	
        formatted = use_case.execute(ids=note_ids, tags=tags, fields=fields, entire=entire)
        console.read(formatted)
    except NotesNotFoundError as e:
    	console.error(e)
    	raise typer.Exit(code=2)
    except InvalidNoteError as e:
        console.error(e)
        raise typer.Exit(code=2)
    except EmptyStorageError as e:
        console.error(e)
        raise typer.Exit(code=2)