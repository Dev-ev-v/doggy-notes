from doggy_notes.domain.exceptions.note_errors import (
    EmptyStorageError,
    NotesNotFoundError,
)

from doggy_notes.presentation.presenters.note_presenter import (
    ErrorsPresenter,
)

class ListNotesUseCase:

    SORT_DEFAULTS = {
        "title": {
            "reverse": False,
            "description": "A-Z",
        },
        "date": {
            "reverse": True,
            "description": "Recent first",
        },
    }

    SORT_KEYS = {
        "title": lambda n: n.title.lower(),
        "date": lambda n: n.date,
    }

    def __init__(self, service):
        self.service = service

    def execute(
        self,
        tags: list[str] | None = None,
        sort_by: str = "date",
        limit: int | None = None,
        desc: bool | None = None,
    ):
        result = self.service.get(tags=tags)

        if result.is_empty:
            if tags:
                filters = {}
                filters["tags"] = tags
                raise NotesNotFoundError(
                    ErrorsPresenter.format_errors(filters)
                )
            raise EmptyStorageError("Empty storage, create a note first")

        if sort_by not in self.SORT_DEFAULTS:
            raise ValueError(
                f"Invalid sort_by: {sort_by}"
            )

        reverse = (
            desc
            if desc is not None
            else self.SORT_DEFAULTS[sort_by]["reverse"]
        )

        sorted_items = sorted(
            result.items,
            key=self.SORT_KEYS[sort_by],
            reverse=reverse,
        )

        if limit is not None:
            sorted_items = sorted_items[:limit]

        result.items = sorted_items

        if result.groups:
            remaining_ids = set(id(item) for item in sorted_items)
            updated_groups = {}

            for tag, items in result.groups.items():
                filtered_items = [
                    item for item in items
                    if id(item) in remaining_ids
                ]

                if filtered_items:
                    ordered_items = [
                        item for item in sorted_items
                        if item in filtered_items
                    ]
                    updated_groups[tag] = ordered_items

            result.groups = updated_groups

        return result