import re
import typer
from typing import Optional

from doggy_notes.cli.dependencies import get_dependencies

from doggy_notes.domain.exceptions.note_errors import AppError

from doggy_notes.domain.enums.note_field import NoteField


def edit_app(
    note_id: str = typer.Argument(
        help="ID or short_id of the note to edit",
    ),
    field: NoteField = typer.Option(
        NoteField.content,
        "--field",
        "-f",
        help="Field to edit: 'content', 'title', 'description', or 'tags'",
        case_sensitive=False,
    ),
):

    deps = get_dependencies()
    try:
        selector = deps.selector.build_selector(ids=[note_id])

        note = deps.edit_note.resolve_note(selector)

        old_text = getattr(note, field, None)

        if field == NoteField.tags:
        	new_text = deps.edit_note.open_editor(old_text)
        	tags = [t for t in re.split(r'[,\n]+', new_text) if t.strip()]
        	new_text = deps.tag_parser.parse_tags(tags) 
        
        else:
            new_text = deps.edit_note.open_editor(old_text)

        _edit_field(new_text, old_text, note, field, deps)

    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))


def _edit_field(new_text, old_text, note, field, deps):
    if new_text != old_text:
        
        success, error_messages = deps.edit_note.execute(
            note,
            field,
            new_text
        )

        if success:
        	deps.console.success("Note successfully updated")
        	deps.console.panel(deps.note_presenter.resume_note(note))
        	
        	deps.console.write(f"[bold]Previous {field.value}:[/bold] {old_text}")
        	deps.console.write(f"[bold]New {field.value}:[/bold] {new_text}")
        
        if error_messages:
        	deps.console.error(', '.join(error_messages))

    else:
        deps.console.warning("No changes detected")