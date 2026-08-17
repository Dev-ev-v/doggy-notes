import typer
from typing import Optional, List
from rich.text import Text

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import AppError
from doggy_notes.domain.enums.note_field import NoteField
from doggy_notes.domain.enums.mode import Mode

read_app = typer.Typer(help="Read notes")


def _run_read(selector, fields=NoteField.content, entire=False):
    deps = get_dependencies()
    try:
        
        result = deps.read_notes.execute(selector)
        
        formatted = _get_formatted(result, fields, entire, deps)
        
        deps.console.read(formatted)
        
    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))


@read_app.command("id")
def read_by_id(
    note_ids: List[str] = typer.Argument(..., help="Note ID(s) to delete (repeat option for multiple)"),
    fields: list[NoteField] = typer.Option(
        [NoteField.content],
        "--field",
        "-f",
        help="Field to display: 'content', 'title', 'description', or 'tags'",
        case_sensitive=False,
    ),
    entire: bool = typer.Option(
        False,
        "--entire",
        help="Display all fields (title, description, content, and tags)",
    ),
):

    deps= get_dependencies()
    
    selector = deps.selector.build_selector(ids=note_ids)
    _run_read(selector, fields=fields, entire=entire)


@read_app.command("tag")
def read_by_tag(
    tags: Optional[List[str]] = typer.Argument(..., help="Read all notes with these tags (repeat option for multiple)"
    ),
    fields: list[NoteField] = typer.Option(
        [NoteField.content],
        "--field",
        "-f",
        help="Field to display: 'content', 'title', 'description', or 'tags'",
        case_sensitive=False,
    ),
    entire: bool = typer.Option(
        False,
        "--entire",
        help="Display all fields (title, description, content, and tags)",
    ),
    mode: Mode = typer.Option(
        Mode.AND,
        "--mode",
        help="Select the search mode between AND or OR",
        case_sensitive=False,
    ),
):

    deps = get_dependencies()
    
    selector = deps.selector.build_selector(tags=tags, mode=mode)
    _run_read(selector, fields=fields, entire=entire)
    
    
@read_app.command("title")
def read_by_titles(
    titles: Optional[List[str]] = typer.Argument(..., help="Read all notes with these title (repeat option for multiple)"
    ),
    fields: list[NoteField] = typer.Option(
        [NoteField.content],
        "--field",
        "-f",
        help="Field to display: 'content', 'title', 'description', or 'tags'",
        case_sensitive=False,
    ),
    entire: bool = typer.Option(
        False,
        "--entire",
        help="Display all fields (title, description, content, and tags)",
    ),
):

    deps = get_dependencies()
    
    selector = deps.selector.build_selector(titles=titles)
    _run_read(selector, fields=fields, entire=entire)    


@read_app.command("all")
def read_all(
    fields: list[NoteField] = typer.Option(
        [NoteField.content],
        "--field",
        "-f",
        help="Field to display: 'content', 'title', 'description', or 'tags'",
        case_sensitive=False,
    ),
    entire: bool = typer.Option(
        False,
        "--entire",
        help="Display all fields (title, description, content, and tags)",
    ),
):
	
	deps = get_dependencies()
	
	selector = deps.selector.build_selector()
	_run_read(selector, fields=fields, entire=entire)


def _get_formatted(result, fields, entire, deps):
    text = Text()
    
    if entire:
        notes = [
        	deps.note_presenter.format_detail(note)
    		for note in result.items
		]
        text.append(deps.note_presenter.separate(55).join(notes))
    
    elif fields:
        notes = [
        	deps.note_presenter.format_values(note, fields)
    		for note in result.items
		]
        text.append(deps.note_presenter.separate(55).join(notes))

    else:
        notes = [
        	deps.note_presenter.resume_notes(note)
    		for note in result.items
		]
        text.append(Text("\n\n").join(notes))

    return text