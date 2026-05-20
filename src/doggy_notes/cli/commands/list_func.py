import typer
from typing import Optional, List

from doggy_notes.cli.dependencies import get_service
from doggy_notes.presentation.presenters.note_presenter import NotePresenter
from doggy_notes.cli.console import Console
from doggy_notes.application.use_cases.list_notes import ListNotesUseCase
from doggy_notes.domain.exceptions.note_errors import (
    EmptyStorageError,
    NotesNotFoundError,
)


def list_func(
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        help="Filter notes by tags (repeat option for multiple)",
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum number of notes to display",
    ),
    sort_by: Optional[str] = typer.Option(
        "date",
        "--sort",
        help="Sort by: 'date' (newest first) or 'title' (alphabetical)",
    ),
    desc: Optional[bool] = typer.Option(
        None,
        "--desc",
        help="Inverts the notes result order",
    ),
):
    """
    [bold cyan]List all saved notes or search by tags[/bold cyan]

    Display notes from storage with optional filtering and sorting.
    Without filters, shows all notes ordered by date.

    [bold yellow]EXAMPLES:[/bold yellow]

      List all notes:
        doggy list

      Filter by tags:
        doggy list --tag "work"
        doggy list --tag "work" --tag "urgent"

      Sort alphabetically:
        doggy list --sort title

      Invert results:
        doggy list --tag "market" --tag "list" --desc

      Limit results:
        doggy list --limit 5
        doggy list --tag "api" --limit 10 --sort title

    [bold yellow]OUTPUT:[/bold yellow]
      [12345678] REST Reference (2026-05-17)
      [87654321] Buy milk (2026-05-16)
    """

    service = get_service()
    presenter = NotePresenter()
    console = Console()

    use_case = ListNotesUseCase(service)

    try:
        unique_tags = (
            list(dict.fromkeys(tags))
            if tags
            else None
        )

        result = use_case.execute(
            tags=unique_tags,
            sort_by=sort_by,
            limit=limit,
            desc=desc,
        )

        rendered_items = [
            presenter.format(item)
            for item in result.items
        ]

        if result.groups:
            rendered_groups = {
                tag: [
                    presenter.format(item)
                    for item in items
                ]
                for tag, items in result.groups.items()
            }

            console.list_notes(
                items=rendered_items,
                groups=rendered_groups,
                filters=result.filters,
            )

        else:
            console.list_notes(
                items=rendered_items,
                title="Notes",
                filters=result.filters,
            )

    except EmptyStorageError as e:
        console.error(e)
    except NotesNotFoundError as e:
    	console.error(e)