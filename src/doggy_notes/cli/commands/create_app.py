import typer
from typing import Optional, List

from doggy_notes.domain.exceptions.note_errors import NoteValidationError, SearchFilterError
from doggy_notes.cli.dependencies import get_dependencies

def create_app(
    content: str = typer.Argument(
        help="Main note content (required)"
    ),
    title: Optional[str] = typer.Option(
        "Untitled",
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
    
    deps = get_dependencies()  
    
    try:
        tags = deps.tag_parser.parse_tags(tags) 
        note = deps.create_note.execute(content=content, title=title, description=description, tags=tags)
        
        deps.console.success("Note successfully created")
        deps.console.panel(deps.note_presenter._resume_note(note))
        
    except (NoteValidationError, SearchFilterError) as e:
        deps.console.error(deps.error_presenter.format(e))