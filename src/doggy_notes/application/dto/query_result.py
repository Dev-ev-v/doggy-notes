from dataclasses import dataclass, field
from typing import Any

from doggy_notes.domain.entities.note import Note


@dataclass(slots=True)
class QueryResult:
    items: list[Note]
    groups: dict[str, list[Note]] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.items