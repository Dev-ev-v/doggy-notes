import typer
from typing import Optional, List

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.enums.sort_direction import SortDirection
from doggy_notes.domain.enums.sort_by import SortBy

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
)

def list_app(
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
    sort_by: SortBy = typer.Option(
        SortBy.date,
        "--sort",
        help="Sort by: 'date' (newest first) or 'title' (alphabetical)",
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
        unique_tags = deps.tag_parser.parse_tags(tags)

        result, warnings = deps.list_notes.resolve_notes(
            tags=unique_tags,
            sort_by=sort_by,
            limit=limit,
            order=order,
            mode=mode,
        )
     
        for warn in warnings:
        	deps.console.warning(warn)

        rendered_items = [
            deps.note_presenter._resume_note(item)
            for item in result.items
        ]
        
        rendered_groups = _get_rendered_groups(result, deps)

        deps.console.list_notes(
            items=rendered_items,
            groups=rendered_groups,
            filters=result.filters,
        )

    except (NoteEmptyStorageError, SearchFilterError, NoteNotFoundError,) as e:
        deps.console.error(deps.error_presenter.format(e))
        

def _get_rendered_groups(result, deps):	
	if result.groups:
	   rendered_groups = {
            tag: [
                deps.note_presenter._resume_note(item)
                for item in items
            ]
            for tag, items in result.groups.items()
	   }
	
	else:
		rendered_groups = {}
    	
	return rendered_groups