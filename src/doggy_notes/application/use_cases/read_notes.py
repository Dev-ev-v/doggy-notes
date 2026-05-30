from rich.text import Text

from doggy_notes.cli.console import Console

from doggy_notes.presentation.presenters.note_presenter import NotePresenter, ErrorsPresenter

from doggy_notes.domain.exceptions.note_errors import (
	NoteEmptyStorageError,
	SearchFilterError,
	NoteNotFoundError,
)


class ReadNotesUseCase:

    def __init__(self, service):
        self.service = service

    def execute(
        self,
        ids: list[str] | None = None,
        tags: list[str] | None = None,
        fields: list[str] = None,
        entire: bool = False,
        mode: str = "AND",
    ) -> Text:

        presenter = NotePresenter()
        console = Console()

        result = self.service.get(ids=ids, tags=tags, mode=mode)

        if result.is_empty:
            if tags or ids:
                filters = {}
                if tags:
                    filters["tags"] = tags
                if ids:
                    filters["ids"] = ids
                raise NoteNotFoundError(
                    ErrorsPresenter.format_errors(filters)
                )
            raise NoteEmptyStorageError("Empty storage, create a note first")

        formatted = Text()
        
        if fields:
        	field_set = set(["title", "description", "tags", "content"])
        	valid_fields = field_set & set(fields)
        	for field in fields:
        	    if field not in valid_fields:
        	    	console.warning(f"{field} is not a valid value of field") 
        	if not valid_fields:
        		console.warning(f"No valid fields, using content")

        for note in result.items:

            if entire:
                formatted.append(
                    presenter.format_detail(note)
                )
                continue

            if fields:              	
            	if valid_fields:
            		values = {}
            		for field in valid_fields:
            			value = getattr(note, field, None)
            			if not value:
            				value = f"No {field}"            
            			if isinstance(value, list):
            				value = ", ".join(value)
            			values[field] = value
            		formatted.append(presenter.format(note, values))
            		continue
            
            formatted.append(presenter.format(note, {"content": note.content}))

        return formatted