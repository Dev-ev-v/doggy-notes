import os
import tempfile
import subprocess
import typer
from typing import Optional
from doggy_notes.domain.entities.note import Note
from doggy_notes.cli.dependencies import get_service
from doggy_notes.cli.parsers.note_parser import NoteParser
from doggy_notes.presentation.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console
from doggy_notes.application.use_cases.edit_note import EditNoteUseCase
from doggy_notes.domain.exceptions.note_errors import (
	NotesNotFoundError,
	InvalidNoteError,
)

def open_editor(initial_text: str) -> str:
    """
    Open the user's default editor with pre-filled text
    and return the edited content.
    """

    # Try to detect the user's preferred editor.
    # Fallback to nano on Unix and notepad on Windows.
    editor = (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or ("notepad" if os.name == "nt" else "nano")
    )

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        suffix=".txt",
        mode="w+",
        delete=False,
        encoding="utf-8",
    ) as temp_file:

        # Fill file with existing note text
        temp_file.write(initial_text)

        # Force write to disk
        temp_file.flush()

        # Store file path
        temp_path = temp_file.name

    try:
        # Open editor and wait until user closes it
        subprocess.run([editor, temp_path], check=True)

        # Read edited text
        with open(temp_path, "r", encoding="utf-8") as file:
            edited_text = file.read()

    finally:
        # Delete temp file even if error happens
        os.unlink(temp_path)

    return edited_text

def edit(
    note_id: str = typer.Argument(
        help="ID or short_id of the note to edit",
    ),
    field: str = typer.Option(
        "content",
        "--field",
        "-f",
        help="Field to edit: 'content', 'title', 'description', or 'tags'",
    ),
):
    """
[bold cyan]Edit a specific field in an existing note[/bold cyan]

Modify note metadata or content interactively
 Opens your default editor for better experience

[bold yellow]EXAMPLES:[/bold yellow]

  Edit note content:
    doggy edit 12345678
    doggy edit 12345678 --field content

  Edit title:
    doggy edit 12345678 --field title

  Edit tags:
    doggy edit 12345678 --field tags

  Edit description:
    doggy edit 12345678 --field description

[bold yellow]FIELDS:[/bold yellow]
  [bold]content[/bold]      Main note text (opens editor)
  [bold]title[/bold]        Note title (max 100 chars)
  [bold]description[/bold]  Additional details (opens editor)
  [bold]tags[/bold]         Tags for filtering

[bold yellow]OUTPUT:[/bold yellow]
  [bold green][OK] Note successfully updated[/bold green]
  [12345678] REST Reference (2026-05-17)
  [bold]Previous tags:[/bold] api, documentation
  [bold]New tags:[/bold] api, documentation, projects, CLI
"""
    service = get_service()
    parser = NoteParser()
    presenter = NotePresenter()
    console = Console()
    use_case = EditNoteUseCase(service)
    try:
    	VALID_FIELDS = {"content", "title", "description", "tags"}
    	if field not in VALID_FIELDS:
    		if field == "id":
    			raise InvalidNoteError("field", "ID cannot be changed")
    		else:
    			raise InvalidNoteError("field", f"{field} is not a valid value of note")
    	note_id = parser.parse_id(note_id)
    	note = use_case.resolve_note(note_id)
    	value = getattr(note, field, None)
    	old_text = getattr(note, field, None) if value else ""
    	if field == "tags":
    		new_text = open_editor(",".join(old_text))
    	else:
    		new_text = open_editor(old_text)

    	if new_text != old_text:
    		use_case.execute(
    			note, 
    			field, 
    			new_text
    		) 
    		console.success("Note successfully updated")
    		console.note(presenter.format(note))
    		console.write(f"[bold]Previous {field}:[/bold] {old_text}")
    		console.write(f"[bold]New {field}:[/bold] {new_text}")
    	else:
    		console.warning("No changes detected")   	    	
    except NotesNotFoundError as e:
    	console.error(e)
    	raise typer.Exit(code=2)
    except InvalidNoteError as e:
    	console.error(e)
    	raise typer.Exit(code=2)