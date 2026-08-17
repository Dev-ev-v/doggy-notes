import typer
from typing import List, Optional

from doggy_notes.domain.exceptions.note_errors import AppError
from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.enums.mode import Mode

delete_app = typer.Typer(help="Add notes to trash")


def _run_delete(selector, yes: bool):
    deps = get_dependencies()
    try:
        result = deps.resolver.resolve(selector)
        notes = result.items
        confirmed = yes or deps.console.confirm(
            f"{len(notes)} notes will be added to trash. Continue?"
        )
        if not confirmed:
            deps.console.error("Operation cancelled")
            return

        deps.delete_notes.execute(notes)
        deps.console.success(f"{len(notes)} successfully added to trash")

        formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
        deps.console.list_notes(formatted_notes, "Notes added to trash")

    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))


@delete_app.command("id")
def delete_by_id(
    note_ids: List[str] = typer.Argument(..., help="Note ID(s) to delete"),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    deps = get_dependencies()
    
    selector = deps.selector.build_selector(ids=note_ids)
    _run_delete(selector, yes=yes)


@delete_app.command("tag")
def delete_by_tag(
    tags: List[str] = typer.Argument(..., help="Tag(s) to filter notes for deletion"),
    mode: Mode = typer.Option(Mode.AND, "--mode", case_sensitive=False),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    deps = get_dependencies()
    
    selector = deps.selector.build_selector(tags=tags, mode=mode)
    _run_delete(selector, yes=yes)


@delete_app.command("title")
def delete_by_title(
    titles: list[str] = typer.Argument(..., help="Titles (or part of it) to search notes for deletion"),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    deps = get_dependencies()
    
    selector = deps.selector.build_selector(titles=titles)
    _run_delete(selector, yes=yes)


@delete_app.command("all")
def delete_all(
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    deps = get_dependencies()
    selector = deps.selector.build_selector()
    _run_delete(selector, yes=yes)