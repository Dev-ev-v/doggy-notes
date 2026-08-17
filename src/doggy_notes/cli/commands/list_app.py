import typer
from typing import Optional, List

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.enums.sort_direction import SortDirection
from doggy_notes.domain.enums.sort_by import SortBy

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import AppError

def list_app(
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        help="Filter notes by tags (repeat option for multiple)",
    ),
    titles: Optional[List[str]] = typer.Option(
    	None,
    	"--title",
    	help="Title to select notes (repeat option for multiple)",    
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help="Maximum number of notes to display",
    ),
    sort_by: SortBy = typer.Option(
        SortBy.created_at,
        "--sort",
        help="Sort by: 'created_at' (newest first) or 'title' (alphabetical)",
        case_sensitive=False,
    ),
    order: SortDirection = typer.Option(
        None,
        "--order",
        case_sensitive=False,
    ),
    mode: Mode = typer.Option(
        Mode.AND,
        "--mode",
        help="Select the search mode between AND or OR",
        case_sensitive=False,
    ),
):
    
    deps = get_dependencies()
    try:       
        selector = deps.selector.build_selector(tags=tags, titles=titles, mode=mode)

        result, warnings = deps.list_notes.resolve_notes(
        	selector,
            sort_by=sort_by,
            limit=limit,
            order=order,
        )
     
        for warn in warnings:
        	deps.console.warning(warn)

        rendered_items = [
            deps.note_presenter.resume_note(item)
            for item in result.items
        ]
        
        rendered_groups = _get_rendered_groups(result, deps)

        deps.console.list_notes(
            items=rendered_items,
            groups=rendered_groups,
            filters=result.filters,
        )

    except AppError as e:
        deps.console.error(deps.error_presenter.format(e))
        

def _get_rendered_groups(result, deps):	
	if result.groups:
	   rendered_groups = {
            i: [
                deps.note_presenter.resume_note(item)
                for item in items
            ]
            for i, items in result.groups.items()
	   }
	
	else:
		rendered_groups = {}
    	
	return rendered_groups