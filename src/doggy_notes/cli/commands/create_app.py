import typer
from typing import Optional, List

from doggy_notes.domain.exceptions.note_errors import AppError
from doggy_notes.cli.dependencies import get_dependencies

def create_app(
    content: str = typer.Argument(
    	None,
        help="Main note content",
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
        
        data = {
        	"content": content,
        	"title": title,
        	"description": description,
        	"tags": tags        
        }
        
        deps.create_note.valid_data(data)
        
        note = deps.create_note.generate_note(data)
        
        success, error_messages = deps.create_note.execute(note)
        
        if success:
        	deps.console.success("Note successfully created")
        	deps.console.panel(deps.note_presenter.resume_note(note))
        
        if error_messages:
        	deps.console.error(', '.join(error_messages))
        
    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))