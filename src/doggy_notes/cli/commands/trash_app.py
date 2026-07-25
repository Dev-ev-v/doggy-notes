import typer
from typing import List, Optional

from doggy_notes.domain.exceptions.note_errors import SearchFilterError, NoteNotFoundError, NoteEmptyStorageError, NoteAmbiguousIDError, NoteOperationError

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.enums.mode import Mode

trash_app = typer.Typer(help="Manage notes inside trash")


@trash_app.command("list")
def list_trash(
	tags: List[str] = typer.Option(
		None, 
		"--tag", 
		help="Tag(s) to filter notes inside trash"),
    mode: Mode = typer.Option(
    	Mode.AND, 
    	"--mode", 
    	help="AND or OR search mode")
):
	
	deps = get_dependencies()
	
	try:
	    parsed_tags = deps.tag_parser.parse_tags(tags)
	    
	    result = deps.trash_notes.resolve_notes(
	        tags=parsed_tags, 
	        mode=mode
	    )
	    
	    notes = result.items
	    
	    formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
	    
	    deps.console.list_notes(formatted_notes, "Notes inside trash")
	
	except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError, NoteAmbiguousIDError) as e:
		deps.console.error(deps.error_presenter.format(e))


@trash_app.command("restore")
def restore(
	tags: List[str] = typer.Option(
		None, 
		"--tag",
		help="Tag(s) to filter notes to restore"),
    mode: Mode = typer.Option(
    	Mode.AND, 
    	"--mode", 
    	help="AND or OR search mode"),
	note_ids: List[str] = typer.Option(
		None, 
		"--id",
		help="Note ID(s) to restore"),
    yes: bool = typer.Option(
    	False, 
    	"--yes", 
    	"-y", 
    	help="Skip confirmation prompt")
):
	
	deps = get_dependencies()
	try:
	    if tags and note_ids:
	    	raise NoteOperationError("Select one selection method: use tag or id, not both")
	    parsed_ids = deps.id_parser.parse_ids(note_ids)
	    parsed_tags = deps.tag_parser.parse_tags(tags)
	    
	    result = deps.trash_notes.resolve_notes(
	        ids=parsed_ids,
	        tags=parsed_tags, 
	        mode=mode
	    )
	    
	    notes = result.items
	    
	    confirmed = yes or deps.console.confirm(f"{len(notes)} notes will be restored. Continue?")
	    if not confirmed:
	        deps.console.error("Operation cancelled")
	        return
	    deps.trash_notes.restore(notes)
	    
	    deps.console.success(f"{len(notes)} successfully restored")
	    
	    formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
	    
	    deps.console.list_notes(formatted_notes, "Restored notes")
	
	except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError, NoteAmbiguousIDError, NoteOperationError) as e:
		deps.console.error(deps.error_presenter.format(e))


@trash_app.command("delete")
def delete(
	note_ids: List[str] = typer.Option(
		None,
		"--id", 
		help="Note ID(s) to delete"),
	all: bool = typer.Option(
		False,
		"--all",
		help="Select all notes from storage to delete"),
    yes: bool = typer.Option(
    	False, 
    	"--yes", 
    	"-y", 
    	help="Skip confirmation prompt")
):
	
	deps = get_dependencies()
	try:
	    parsed_ids = deps.id_parser.parse_ids(note_ids)
	    if not parsed_ids and not all:
	    	raise NoteOperationError("No notes selected")
	    
	    result = deps.trash_notes.resolve_notes(
	        ids=parsed_ids,
	    )
	    
	    notes = result.items
	    
	    confirmed = yes or deps.console.confirm(f"{len(notes)} notes will be PERMANENTLY DELETED. Continue?")
	    if not confirmed:
	        deps.console.error("Operation cancelled")
	        return
	    
	    deps.console.write("Deleting the selected notes, press 'q' to cancel")	    
	    extra_confirmation = deps.console.confirm_with_countdown()
	    
	    if not extra_confirmation:
	    	return 
	    	
	    deps.trash_notes.delete(notes)
	    
	    deps.console.success(f"{len(notes)} successfully deleted")
	    
	    formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
	    
	    deps.console.list_notes(formatted_notes, "Deleted notes")
	
	except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError, NoteAmbiguousIDError, NoteOperationError) as e:
		deps.console.error(deps.error_presenter.format(e))