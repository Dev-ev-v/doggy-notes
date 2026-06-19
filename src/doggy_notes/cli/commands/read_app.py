import typer
from typing import Optional, List
from rich.text import Text

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
)
from doggy_notes.domain.enums.note_field import NoteField
from doggy_notes.domain.enums.mode import Mode

read_app = typer.Typer(help="Read notes")


def _run_read(*, note_ids=None, tags=None, fields=NoteField.content, entire=False, mode="AND"):
    deps = get_dependencies()
    try:
        parsed_ids = deps.id_parser.parse_ids(note_ids)
        parsed_tags = deps.tag_parser.parse_tags(tags)
        
        result = deps.read_notes.resolve_notes(ids=parsed_ids, tags=parsed_tags, mode=mode)
        
        formatted = _get_formatted(result, fields, entire, deps)
        
        deps.console.read(formatted)
        
    except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError,) as e:
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

    _run_read(note_ids=note_ids, fields=fields, entire=entire)


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

    _run_read(tags=tags, fields=fields, entire=entire, mode=mode)


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
	
	_run_read(fields=fields, entire=entire)


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
        	deps.note_presenter._resume_notes(note)
    		for note in result.items
		]
        text.append(Text("\n\n").join(notes))

    return text