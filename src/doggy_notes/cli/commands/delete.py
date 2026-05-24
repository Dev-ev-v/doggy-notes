import typer
from typing import Optional, List
from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import (
    EmptyStorageError,
    NotesNotFoundError,
    InvalidNoteError,
)

def delete(
    note_ids: Optional[List[str]] = typer.Option(
        None,
        "--id",
        help="Note ID(s) to delete (repeat option for multiple)",
    ),
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        help="Delete all notes with these tags (repeat option for multiple)",
    ),
    delete_all: bool = typer.Option(
        False,
        "--all",
        help="Delete all notes in storage",
    ),
):
    """
[bold cyan]Delete notes from storage by ID, short_id, or tags[/bold cyan]

Remove notes using flexible filters. Operations require confirmation
before execution.

[bold yellow]EXAMPLES:[/bold yellow]

  Delete by ID:
    doggy delete --id 12345678
    doggy delete --id abc123 --id def456

  Delete by tags:
    doggy delete --tag "archive"
    doggy delete --tag "temp" --tag "old"

  Delete all notes:
    doggy delete --all

[bold yellow]OUTPUT:[/bold yellow]

  [12345678] REST Reference (2026-05-17)
  [23456789] supermarket list (2026-05-17)
  [34567890] to my dear friend Pedro (2026-05-17)
  [45678901] A good day (2026-05-17)
  [56789012] JSON vs SQL (2026-05-17)
  
  [bold yellow][!] 5 notes will be deleted. Continue? [y/N][/bold yellow]
  y, n: y
  [bold green][OK] 5 notes deleted[/bold green]
"""
    deps = get_dependencies()
    try:
        if all and note_ids or all and tags:
        	raise InvalidNoteError("args", "Use --all without any other selection methods")
        if note_ids:
        	note_ids = [deps.parser.parse_id(id) for id in note_ids]
        	note_ids = list(dict.fromkeys(note_ids))
        if tags:
        	tags = deps.parser.parse_tags(tags)  
        if not note_ids and not tags:
        	if not delete_all:
        		raise InvalidNoteError("args", "Use --all to delete all saves notes or a valid filter")      	
        result = deps.delete_notes.resolve_notes(
        	ids=note_ids,
            tags=tags,
            delete_all=delete_all,
        )
        confirmed = deps.delete_notes.get_confirmation(result)
        if not confirmed:
            deps.console.error("Operation cancelled")
            return
        deps.delete_notes.execute(result)
        deps.console.success(f"Notes deleted")
    except NotesNotFoundError as e:
    	deps.console.error(f"Invalid filters - {e}")
    	raise typer.Exit(code=2)
    except EmptyStorageError as e:
   	 deps.console.error(f"No notes found - {e}")
    except InvalidNoteError as e:
        deps.console.error(e)
    