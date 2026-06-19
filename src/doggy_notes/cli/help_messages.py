class HelpMessages():

    LIST_APP_MESSAGE = """
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

    INFO_APP_MESSAGE = "[bold cyan]Show detailed information about the installation and environment[/bold cyan]"

    CREATE_APP_MESSAGE = """
[bold cyan]Create a note and save it in data_dir[/bold cyan]

Store notes quickly with optional metadata.

[bold yellow]EXAMPLES:[/bold yellow]

  Basic:
    doggy add "Remember to buy milk"

  Complete:
    doggy add "API Endpoints" /
     --title "REST Reference" /
     --tag api /
     --tag documentation /
      -d "Quick reference for v2 endpoints"

[bold yellow]OUTPUT:[/bold yellow]
  [bold green][OK] Note successfully created[/bold green]
  [12345678] REST Reference (2026-05-17)        
"""

    DELETE_APP_MESSAGE = """
[bold cyan]Delete notes from storage by ID, short_id, or tags[/bold cyan]

Remove notes using flexible filters. Operations require confirmation
before execution.

[bold yellow]EXAMPLES:[/bold yellow]

  Delete by ID:
    doggy delete --id 12345678
    doggy delete --id abc123 --id def456

  Delete by tags:
    doggy delete --tag "archive"
    doggy delete --tag "temp" --tag "old"

  Delete all notes:
    doggy delete --all

[bold yellow]OUTPUT:[/bold yellow]

  [12345678] REST Reference (2026-05-17)
  [23456789] supermarket list (2026-05-17)
  [34567890] to my dear friend Pedro (2026-05-17)
  [45678901] A good day (2026-05-17)
  [56789012] JSON vs SQL (2026-05-17)
  
  [bold yellow][!] 5 notes will be deleted. Continue? [y/N][/bold yellow]
  y, n: y
  [bold green][OK] 5 notes deleted[/bold green]
"""

    READ_APP_MESSAGE = """
[bold cyan]Display specific fields from a note or all its contents. Display all noted by default[/bold cyan]

Read notes data without editing. Shows formatted output with metadata
and content clearly separated. 

[bold yellow]EXAMPLES:[/bold yellow]

  Read note content (default):
    doggy read
    doggy read --id 12345678
    doggy read --id 12345678 --field content

  Read multiple fields:
    doggy read --field tags
    doggy read --id 12345678 --field title --field tags
    doggy read --id 12345678 --field title --field description --field tags --field content

  Read all note information:
    doggy read --id 12345678 --entire

  Read notes by tags:
    doggy read --tag work --field title --field tags
    doggy read --tag activities --tag important --tag tomorrow --field description --field content
    
  Read multiple notes by ids:
    doggy read --id 12345678 --id 23456789 --entire

[bold yellow]FIELDS:[/bold yellow]

  [bold]content[/bold]      Main note text
  [bold]title[/bold]        Note title
  [bold]description[/bold]  Additional details
  [bold]tags[/bold]         Associated tags

[bold yellow]OUTPUT:[/bold yellow]

  [bold cyan]Single field:[/bold cyan]
    [12345678] REST Reference (2026-05-17)
    
    Content: API Endpoints documentation for v2 integration...

  [bold cyan]All fields (--entire):[/bold cyan]
    [bold]ID:[/bold]          12345678
    [bold]Title:[/bold]       REST Reference
    [bold]Created:[/bold]     2026-05-17
    [bold]Tags:[/bold]       api, documentation
    
    [bold]Description:[/bold]
    Quick reference for v2 endpoints
    
    [bold]Content:[/bold]
    API Endpoints documentation for v2 integration...
"""

    PATH_APP_MESSAGE = "Path app"