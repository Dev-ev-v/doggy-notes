from dataclasses import dataclass
from typing import Optional

from doggy_notes.domain.exceptions.note_errors import InvalidNoteError
from doggy_notes.application.dto.query_result import QueryResult


@dataclass
class NoteServiceConfig:
    max_title_length: int = 100
    short_id_length: int = 8


class NoteService:
    def __init__(self, repo, config: Optional[NoteServiceConfig] = None):
        self.repo = repo
        self.config = config or NoteServiceConfig()

    def create(self, note):
        self._validate_note(note)
        self.repo.create(note)

    def update(self, note):
        self._validate_note(note)
        self.repo.update(note)

    def delete(self, note):
        self.repo.delete(note)

    def get(
        self,
        ids: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> QueryResult:
        if ids and tags:
            raise InvalidNoteError(
                "filter",
                "Use ids OR tags, not both"
            )

        if ids:
            return self._get_by_ids(ids)

        if tags:
            return self._get_by_tags(tags)

        return self._get_all()

    def _validate_note(self, note):
        if not note.title:
            return

        if len(note.title) > self.config.max_title_length:
            raise InvalidNoteError(
                "title",
                f"Title exceeds maximum length of {self.config.max_title_length}"
            )

    def _get_by_ids(self, ids: list[str]) -> QueryResult:
        groups = {
            id: self._fetch_by_id(id)
            for id in ids
        }
        items = self._flatten_groups(groups)
        return QueryResult(
            items=items,
            groups=groups,
            filters={"ids": ids},
        )

    def _get_by_tags(self, tags: list[str]) -> QueryResult:
        groups = {}
        for tag in tags:
            result = self.repo.get_by_tag(tag)
            groups[tag] = result if isinstance(result, list) else [result] if result else []
        items = self._flatten_groups(groups)
        return QueryResult(
            items=items,
            groups=groups,
            filters={"tags": tags},
        )

    def _get_all(self) -> QueryResult:
        items = self.repo.get_all()
        return QueryResult(
            items=items,
            groups={},
            filters={},
        )

    def _fetch_by_id(self, id: str):
        is_short_id = len(id) == self.config.short_id_length
        result = (
            self.repo.get_by_short_id(id)
            if is_short_id
            else self.repo.get_by_id(id)
        )
        return result if isinstance(result, list) else [result] if result else []

    def _flatten_groups(self, groups: dict) -> list:
        items = []
        for value in groups.values():
            if isinstance(value, list):
                items.extend(value)
            elif value is not None:
                items.append(value)
        return items