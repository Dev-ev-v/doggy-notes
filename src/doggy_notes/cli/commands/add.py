import typer

from typing import Optional, List
from datetime import datetime

from doggy_notes.domain.note import Note
from doggy_notes.cli.dependencies import get_service

app = typer.Typer()


@app.command(help="Create a new note.")
def add(
    content: str,
    title: Optional[str] = typer.Option(None, "--title"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    tags: Optional[List[str]] = typer.Option(None, "--tags")
):
    service = get_service()

    note = Note(
        content=content,
        title=title,
        description=description,
        tags=tags,
        date=datetime.now()
    )

    service.create_note(note)