from typing import Protocol

from doggy_notes.domain.value_objects.note_selector import NoteSelector
from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError, NoteEmptyStorageError

class QueryStrategy(Protocol):
	def matches(self, selector: NoteSelector) -> bool: ...
	def fetch(self, repo, selector: NoteSelector, trash: bool) -> QueryResult: ...
	def not_found_error(self, selector: NoteSelector, trash: bool) -> NoteNotFoundError | NoteEmptyStorageError: ...	