import typer
from typing import List, Optional

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import SearchFilterError, NoteNotFoundError, NoteEmptyStorageError
from doggy_notes.domain.enums.mode import Mode

delete_app = typer.Typer(help="Delete notes")


def _run_delete(*, note_ids=None, tags=None, mode="AND", yes: bool):
    deps = get_dependencies()
    try:
        parsed_ids = deps.id_parser.parse_ids(note_ids)
        parsed_tags = deps.tag_parser.parse_tags(tags)
        
        result = deps.delete_notes.resolve_notes(
            ids=parsed_ids,
            tags=parsed_tags,
            mode=mode,
        )

        confirmed = yes or deps.console.confirm(f"{len(result.items)} notes will be deleted. Continue?")
        if not confirmed:
            deps.console.error("Operation cancelled")
            return

        deps.delete_notes.execute(result)
        deps.console.success("Notes deleted")

    except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError) as e:
        deps.console.error(deps.error_presenter.format(e))


@delete_app.command("id")
def delete_by_id(
    note_ids: List[str] = typer.Argument(..., help="Note ID(s) to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
 
    _run_delete(note_ids=note_ids, yes=yes)


@delete_app.command("tag")
def delete_by_tag(
    tags: List[str] = typer.Argument(..., help="Tag(s) to filter notes for deletion"),
    mode: Mode = typer.Option(Mode.AND, "--mode", help="AND or OR search mode", case_sensitive=False),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    
    _run_delete(tags=tags, mode=mode, yes=yes)


@delete_app.command("all")
def delete_all(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    
    _run_delete(yes=yes)