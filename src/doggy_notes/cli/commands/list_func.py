import typer
from typing import Optional, List
from dataclasses import field
from doggy_notes.infra.paths import build_paths

from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)


def list_func(
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
    sort_by: Optional[str] = typer.Option(
        "date",
        "--sort",
        help="Sort by: 'date' (newest first) or 'title' (alphabetical)",
    ),
    asc: Optional[bool] = typer.Option(
        None,
        "--asc",
        help="Sort in ascending order",
    ),
    desc: Optional[bool] = typer.Option(
        None,
        "--desc",
        help="Sort in descending order",
    ),
    mode: Optional[str] = typer.Option(
    	"AND",
    	"--mode",
    	help="Select the search mode between AND or OR",
    ),
    path: Optional[str] = typer.Option(
		None,
		"--path",
		help="Lists a path from doggy-notes"    
    )
):
    """
    [bold cyan]List all saved notes or search by tags[/bold cyan]

    Display notes from storage with optional filtering and sorting.
    Without filters, shows all notes ordered by date.

    [bold yellow]EXAMPLES:[/bold yellow]

      List all notes:
        doggy list

      Filter by tags:
        doggy list --tag "work"
        doggy list --tag "work" --tag "urgent"

      Sort alphabetically:
        doggy list --sort title

      Sort in ascending or descending order:
        doggy list --tag "market" --tag "list" --asc
        doggy list --tag foods --tag cheap --sort title -- desc

      Limit results:
        doggy list --limit 5
        doggy list --tag "api" --limit 10 --sort title

    [bold yellow]OUTPUT:[/bold yellow]
      [12345678] REST Reference (2026-05-17)
      [87654321] Buy milk (2026-05-16)
      
    [bold yellow]MORE INFO[/bold yellow]
      Sort options and default sort order:
        - date(default): desc(recents first)
        - title: asc(A-Z) 	
    """
    deps = get_dependencies()
    try:      	  	
        #ASC AND DESC
        if asc and desc:
       	 deps.console.warning("Got both --asc and --desc, using --asc")
       	 asc = True
       	 desc = None
        #LIMIT
        if isinstance(limit, int):
        	if limit <= 0:
        		deps.console.warning("Invalid --limit, must be higher than 0")
        		limit = None
        
        unique_tags = deps.parser.parse_tags(tags)

        result = deps.list_notes.execute(
            tags=unique_tags,
            sort_by=sort_by,
            limit=limit,
            asc=asc,
            desc=desc,
            mode=mode,
        )

        rendered_items = [
            deps.presenter.format(item)
            for item in result.items
        ]

        if result.groups:
            rendered_groups = {
                tag: [
                    deps.presenter.format(item)
                    for item in items
                ]
                for tag, items in result.groups.items()
            }

            deps.console.list_notes(
                items=rendered_items,
                groups=rendered_groups,
                filters=result.filters,
            )

        else:
            deps.console.list_notes(
                items=rendered_items,
                title="Notes",
                filters=result.filters,
            )

    except NoteEmptyStorageError as e:
        deps.console.error(e)
    except NoteNotFoundError as e:
    	deps.console.error(e)
    except SearchFilterError as e:
    	deps.console.error(e)