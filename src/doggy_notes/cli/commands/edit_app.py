import os
import re
import tempfile
import subprocess
import typer
from typing import Optional

from doggy_notes.cli.dependencies import get_dependencies

from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
)

from doggy_notes.domain.enums.note_field import NoteField


def open_editor(initial_text: str) -> str:
    editor = (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or ("notepad" if os.name == "nt" else "nano")
    )

    with tempfile.NamedTemporaryFile(
        suffix=".txt",
        mode="w+",
        delete=False,
        encoding="utf-8",
    ) as temp_file:

        temp_file.write(initial_text)

        temp_file.flush()

        temp_path = temp_file.name

    try:
        subprocess.run([editor, temp_path], check=True)

        with open(temp_path, "r", encoding="utf-8") as file:
            edited_text = file.read()

    finally:
        os.unlink(temp_path)

    return edited_text


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
        note_id = deps.id_parser.parse_id(note_id)

        note = deps.edit_note.resolve_note(note_id)

        old_text = getattr(note, field, None)

        if field == NoteField.tags:
        	new_text = open_editor(",".join(old_text))
        	tags = [t for t in re.split(r'[,\n]+', new_text) if t.strip()]
        	new_text = deps.tag_parser.parse_tags(tags) 
        else:
            new_text = open_editor(old_text)

        _edit_field(new_text, old_text, note, field, deps)

    except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError,) as e:
        deps.console.error(deps.error_presenter.format(e))


def _edit_field(new_text, old_text, note, field, deps):
    if new_text != old_text:
        deps.edit_note.execute(
            note,
            field,
            new_text
        )

        deps.console.success("Note successfully updated")
        deps.console.panel(deps.note_presenter._resume_note(note))

        deps.console.write(f"[bold]Previous {field.value}:[/bold] {old_text}")
        deps.console.write(f"[bold]New {field.value}:[/bold] {new_text}")

    else:
        deps.console.warning("No changes detected")