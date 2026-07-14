import typer
from typing import Optional, List
from pathlib import Path

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import NoteImportationError, NoteValidationError


def import_app(
    output_path: Path = typer.Argument(None, help="File path"),
    import_all: bool = typer.Option(False, "--all", help="Imports all export files from a dir"),
):
    deps = get_dependencies()

    try:
        output_path = deps.legacy_importer.resolve_output_path(output_path)

        _run_import(output_path, import_all, deps)

    except (NoteImportationError, NoteValidationError) as e:
        deps.console.error(e)	


def _run_import(output_path: Path, import_all, deps):
	
	saved_notes = []
	error_messages = []
	
	if output_path.is_file():
		notes, errors, skipped_data = _import_file(output_path, deps)
	
	elif output_path.is_dir():		
		if import_all:
			_import_all_dir(output_path, deps)
			return		
		
		else:
			notes, errors, skipped_data = _import_last_file(output_path, deps)
			
	else:
		raise NoteImportationError("Invalid file format, not a file or a directory")
	
	saved_notes.extend(notes)	
	error_messages.extend(errors)
	
	
	
	_format_output(saved_notes, error_messages, skipped_data, deps)
		
	
def _import_file(output_path, deps):
	is_valid_file = deps.legacy_importer.valid_file(output_path)
		
	if is_valid_file:
		notes, errors, skipped_data = deps.legacy_importer.import_json_note(output_path)
		
	else:
		raise NoteImportationError(f"File {output_path.name} does not have a valid format")
		
	return notes, errors, skipped_data
	

def _import_all_dir(output_path, deps):
    saved_notes = []
    error_messages = []
    skipped_all = []

    for file in output_path.glob("*.json"):
        notes, errors, skipped_data = deps.legacy_importer.import_json_note(file)
        saved_notes.extend(notes)
        error_messages.extend(errors)
        skipped_all.extend(skipped_data)

    _format_output(saved_notes, error_messages, skipped_all, deps)
			

def _import_last_file(output_path, deps):
	latest = deps.legacy_importer._get_latest_export(output_path)
			
	if latest:
		notes, errors, skipped_data = deps.legacy_importer.import_json_note(latest)
		
	else:
		raise NoteImportationError(f"No exportations found in {output_path.name}")
		
	return notes, errors, skipped_data
	

def _format_output(saved_notes, error_messages, skipped_data, deps):
	
	if saved_notes:
		formatted_notes = _get_formatted_output(notes=saved_notes, deps=deps)
		
		deps.console.write("Imported notes:", style="subtitle")
		deps.console.list_notes(formatted_notes, f"{len(formatted_notes)} notes successfully imported")
	
	else:
		deps.console.error("No notes imported")
	
	if error_messages:
	   deps.console.error(f"{len(error_messages)} errors have been raised")
		
	if skipped_data:
		
		formatted_data = _get_formatted_output(skipped_data=skipped_data, deps=deps)
		
		deps.console.write("Skipped notes:", style="subtitle")
		deps.console.list_notes(formatted_data, f"{len(formatted_data)} notes were not imported")
		

def _get_formatted_output(notes=None, skipped_data=None, deps=None):

    notes = notes or []
    skipped_data = skipped_data or []

    if notes:
        formatted_output = [
            deps.note_presenter.resume_note(note)
            for note in notes
        ]

    elif skipped_data:
        formatted_output = _dedupe_skipped(skipped_data, deps)

    else:
        formatted_output = []

    return formatted_output


def _dedupe_skipped(skipped_data, deps):
    seen = {}

    for data in skipped_data:
        key = (data.preview, data.date, tuple(data.errors))
        seen[key] = seen.get(key, {"data": data, "count": 0})
        seen[key]["count"] += 1

    formatted_output = []
    for entry in seen.values():
        text = deps.note_presenter.resume_data(entry["data"])
        if entry["count"] > 1:
            text += f" (x{entry['count']})"
        formatted_output.append(text)

    return formatted_output