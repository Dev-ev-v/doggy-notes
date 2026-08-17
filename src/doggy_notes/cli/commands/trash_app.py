import typer
from typing import List, Optional

from doggy_notes.domain.exceptions.note_errors import AppError

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
    	help="AND or OR search mode"),
    titles: List[str] = typer.Option(
		None,
		"--title",
		help="Title to match notes")    
):
	
	deps = get_dependencies()
	
	try:
	    selector = deps.selector.build_selector(tags=tags, mode=mode, titles=titles)
	    
	    result = deps.resolver.resolve(selector, trash=True)
	    
	    notes = result.items
	    
	    formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
	    
	    deps.console.list_notes(formatted_notes, "Notes inside trash")
	
	except AppError as e:
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
	titles: List[str] = typer.Option(
		None,
		"--title",
		help="Title to match notes"),
    yes: bool = typer.Option(
    	False, 
    	"--yes", 
    	"-y", 
    	help="Skip confirmation prompt")
):
	
	deps = get_dependencies()
	try:
	    selector = deps.selector.build_selector(tags=tags, mode=mode, ids=note_ids, titles=titles)
	    
	    result = deps.resolver.resolve(selector, trash=True)
	    
	    notes = result.items
	    
	    confirmed = yes or deps.console.confirm(f"{len(notes)} notes will be restored. Continue?")
	    if not confirmed:
	        deps.console.error("Operation cancelled")
	        return
	    deps.trash_notes.restore(notes)
	    
	    deps.console.success(f"{len(notes)} successfully restored")
	    
	    formatted_notes = [deps.note_presenter.resume_note(note) for note in notes]
	    
	    deps.console.list_notes(formatted_notes, "Restored notes")
	
	except AppError as e:
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
	    if not all and not note_ids:
	    	deps.console.error("Select notes to continue this operation")
	    	raise typer.Exit()	    	
	    selector = deps.selector.build_selector(ids=note_ids)
	    
	    result = deps.resolver.resolve(selector, trash=True)
	    
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
	
	except AppError as e:
		deps.console.error(deps.error_presenter.format(e))