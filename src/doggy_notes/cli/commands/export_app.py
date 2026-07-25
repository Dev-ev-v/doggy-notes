import typer
from typing import Optional, List
from pathlib import Path

from doggy_notes.domain.exceptions.note_errors import NoteImportationError, NoteNotFoundError, SearchFilterError, NoteEmptyStorageError, NoteAmbiguousIDError, PathNotFoundError

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.enums.file_format import ExportFileFormat

export_app = typer.Typer(help="Export notes")


def _run_export(*, note_ids=None, tags=None, mode="AND", path=None, format="json"):
    deps = get_dependencies()
    try:
        parsed_ids = deps.id_parser.parse_ids(note_ids)
        parsed_tags = deps.tag_parser.parse_tags(tags)
        
        result = deps.export_notes.resolve_notes(
            ids=parsed_ids,
            tags=parsed_tags,
            mode=mode,
        )
        
        try:
            export_format = ExportFileFormat(format)
        except ValueError:
            valid = ", ".join(f.value for f in ExportFileFormat)
            deps.console.error(f"Invalid format '{format}'. Valid options: {valid}")
            raise typer.Exit(code=1)
        
        output_path = deps.export_notes.resolve_output_path(path)
        file = deps.export_notes.execute(result, output_path, export_format)
        deps.console.success(f"Notes succesfully exported")
        deps.console.panel(str(file))

        
    except (NoteImportationError, NoteNotFoundError, SearchFilterError, NoteEmptyStorageError, NoteAmbiguousIDError, PathNotFoundError) as e:
        deps.console.error(e)


@export_app.command("id")
def export_by_id(
    note_ids: List[str] = typer.Argument(..., help="Note ID(s) to export"),
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
 
    _run_export(note_ids=note_ids, path=path, format=format)


@export_app.command("tag")
def export_by_tag(
    tags: List[str] = typer.Argument(..., help="Tag(s) to filter notes"),
    mode: Mode = typer.Option(Mode.AND, "--mode", help="AND or OR search mode", case_sensitive=False),
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
    
    _run_export(tags=tags, mode=mode, path=path, format=format)


@export_app.command("all")
def export_all(
    path: Path = typer.Option(None, "--path", help="Path to export the selected notes"),
    format: str = typer.Option("json", "--format", help="File format to export"),
):
    
    _run_export(path=path, format=format)			