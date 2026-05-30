import typer
from typing import Optional, List

from doggy_notes.domain.exceptions.note_errors import NoteException
from doggy_notes.cli.dependencies import get_dependencies

def add(
    content: str = typer.Argument(
        help="Main note content (required)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Note title (max 100 chars)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Aditional note details",
    ),
    tags: List[str] = typer.Option(
        None,
        "--tag",
        help="Repeat option to add multiple tags, useful to filter",
    ),
):
    """
[bold cyan]Create a note and save it in data_dir[/bold cyan]

Store notes quickly with optional metadata.

[bold yellow]EXAMPLES:[/bold yellow]

  Basic:
    doggy add "Remember to buy milk"

  Complete:
    doggy add "API Endpoints" /
     --title "REST Reference" /
     --tag api /
     --tag documentation /
      -d "Quick reference for v2 endpoints"

[bold yellow]OUTPUT:[/bold yellow]
  [bold green][OK] Note successfully created[/bold green]
  [12345678] REST Reference (2026-05-17)        
"""
    deps = get_dependencies()  
    
    try:
        if not title:
            title = "Untitled"
            tags = deps.parser.parse_tags(tags) 
        note = deps.create_note.execute(content=content, title=title, description=description, tags=tags)
        deps.console.success("Note successfully created")
        deps.console.note(deps.presenter.format(note))
    except NoteException as e:
        deps.console.error(e)