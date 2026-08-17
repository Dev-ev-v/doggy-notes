import typer
from typing import Optional, List
from pathlib import Path

from doggy_notes.domain.exceptions.note_errors import AppError

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.enums.file_format import ExportFileFormat

export_app = typer.Typer(help="Export notes")


def _run_export(selector, path=None, format="json"):
    deps = get_dependencies()
    try:        
        try:
            export_format = ExportFileFormat(format)
        except ValueError:
            valid = ", ".join(f.value for f in ExportFileFormat)
            deps.console.error(f"Invalid format '{format}'. Valid options: {valid}")
            raise typer.Exit(code=1)
        
        output_path = deps.export_notes.resolve_output_path(path)
        file, notes = deps.export_notes.execute(selector, output_path, export_format)
        deps.console.success(f"{len(notes)} notes succesfully exported")
        formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
        deps.console.list_notes(formatted_notes, "Notes added to trash")
        parts = Path(file).parts
        root_name = parts[-1]
        deps.console.panel(root_name, "File Generated")

        
    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))


@export_app.command("id")
def export_by_id(
    note_ids: List[str] = typer.Argument(..., help="Note ID(s) to export"),
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
 
    deps = get_dependencies()
    selector = deps.selector.build_selector(ids=note_ids)
    
    _run_export(selector, path=path, format=format)


@export_app.command("tag")
def export_by_tag(
    tags: List[str] = typer.Argument(..., help="Tag(s) to filter notes"),
    mode: Mode = typer.Option(Mode.AND, "--mode", help="AND or OR search mode", case_sensitive=False),
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
    
    deps = get_dependencies()
    selector = deps.selector.build_selector(tags=tags, mode=mode)
    
    _run_export(selector, path=path, format=format)


@export_app.command("all")
def export_all(
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
    
    deps = get_dependencies()
    selector = deps.selector.build_selector()
    _run_export(selector, path=path, format=format)			