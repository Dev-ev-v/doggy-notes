import typer
from typing import Optional, List
from pathlib import Path

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import NoteImportationError


def import_app(
    output_path: Path = typer.Argument(None, help="File path"),
    all: bool = typer.Option(False, "--all", help="Imports all exports files from a dir"),
):
    deps = get_dependencies()

    try:
        output_path = deps.legacy_importer.resolve_output_path(output_path)

        _run_import(output_path, all, deps)

    except NoteImportationError as e:
        deps.console.error(e)	


def _run_import(output_path: None, all, deps):
	
	saved_notes = []
	error_messages = []
	
	if output_path.is_file():
		notes, errors, skipped_data = _import_file(output_path, deps)
	
	elif output_path.is_dir():		
		if all:
			_import_all_dir(output_path, deps)
			return		
		
		else:
			notes, errors, skipped_data = _import_last_file(output_path, deps)
	
	saved_notes.extend(notes)	
	error_messages.extend(errors)
	
	_format_output(saved_notes, error_messages, skipped_data, deps)
		
	
def _import_file(output_path, deps):
	is_valid_file = deps.legacy_importer.valid_file(output_path)
		
	if is_valid_file:
		notes, errors, skipped_data = deps.legacy_importer.import_json_note(output_path)
		
	else:
		raise NoteImportationError("File {output_path.name} does not have a valid format")
		
	return notes, errors, skipped_data
	

def _import_all_dir(output_path, deps):
	saved_notes = []
	error_messages = []
	
	for file in output_path.glob("*.json"):
		notes, errors, skipped_data = deps.legacy_importer.import_json_note(file)
				
		saved_notes.extend(notes)		
		error_messages.extend(errors)
			
	_format_output(saved_notes, error_messages, skipped_data, deps)
			

def _import_last_file(output_path, deps):
	latest = deps.legacy_importer._get_latest_export(output_path)
			
	if latest:
		notes, errors, skipped_data = deps.legacy_importer.import_json_note(latest)
		
	else:
		raise NoteImportationError(f"No exportations found in {output_path.name}")
		
	return notes, errors, skipped_data
	

def _format_output(saved_notes, error_messages, skipped_data, deps):
	
	if saved_notes:
		formatted_notes = _get_formatted_notes(notes=saved_notes, deps=deps)
		
		deps.console.write("Imported notes:", style="subtitle")
		deps.console.list_notes(formatted_notes, f"{len(formatted_notes)} notes successfully imported")
	
	else:
		deps.console.error("All selected notes already exist in storage")

	
	if error_messages:
		deps.console.error(f"{len(error_messages)} errors has been raised")
		
	if skipped_data:
		
		formatted_notes = _get_formatted_notes(data=skipped_data, notes_to_skip=saved_notes, deps=deps)
		
		deps.console.write("Skipped notes:", style="subtitle")
		deps.console.list_notes(formatted_notes, f"{len(formatted_notes)} notes were not imported")
		

def _get_formatted_notes(data=None, notes=None, notes_to_skip: list=[], deps=None):
		
	if data:
		clean_data = [deps.legacy_importer.clean(i) for i in data]
		
		notes = [deps.create_note.generate_note(i) for i in clean_data]
		
	saved_ids = {note.id for note in notes_to_skip}
	
	formatted_notes = [
		deps.note_presenter._resume_note(note)
    	for note in notes
   	 if note.id not in saved_ids
	]
	
	return formatted_notes