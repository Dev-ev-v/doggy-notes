from enum import Enum

from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
)

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.enums.sort_direction import SortDirection
from doggy_notes.domain.enums.sort_by import SortBy

class ListNotesUseCase:

    SORT_DEFAULTS = {
        "title": {
            "reverse": False,
            "description": "A-Z",
        },
        "date": {
            "reverse": True,
            "description": "Recent first"
        },
    }

    SORT_KEYS = {
        "title": lambda n: n.title.lower(),
        "date": lambda n: n.date,
    }

    def __init__(self, service):
        self.service = service

    def resolve_notes(
        self,
        tags: list[str] | None = None,
        sort_by: SortBy = SortBy.date,
        limit: int | None = None,
        order: SortDirection = None,
        mode: Mode = Mode.AND,
    ):
        warnings = []
        
        limit_warning = self._check_limit(limit)
        if limit_warning:
        	warnings.append(limit_warning)
        	limit = None
       
        result = self.service.get(tags=tags, mode=mode)

        reverse = self._get_reverse(order, sort_by)

        sorted_items = sorted(
            result.items,
            key=self.SORT_KEYS[sort_by],
            reverse=reverse,
        )

        if limit is not None:
            sorted_items = sorted_items[:limit]

        result.items = sorted_items

        if result.groups:
            result = self._update_groups(result, sorted_items)

        return result, warnings


    def _update_groups(self, result, sorted_items):
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
        
    
    def _get_reverse(self, order, sort_by):
        if not order:
        	reverse = self.SORT_DEFAULTS[sort_by]["reverse"]
        elif order == SortDirection.asc:
            reverse = False
        else:
            reverse = True
        
        return reverse    
    
    
    def _check_limit(self, limit):
        if isinstance(limit, int) and limit <= 0:
        	return "Invalid limit value, must be higher than 0"
        return None                                                                                                                                                                                       