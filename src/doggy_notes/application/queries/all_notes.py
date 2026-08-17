from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.exceptions.note_errors import NoteEmptyStorageError

class AllNotes:
	def matches(self, selector) -> bool:
		return True

	def fetch(self, repo, selector, trash: bool) -> QueryResult:
		items = repo.get_all(trash)
		return QueryResult(
			items=items,
			groups={},
			filters={},
		)

	def not_found_error(self, selector, trash: bool) -> Exception:
		storage = "trash" if trash else "database"
		return NoteEmptyStorageError(f"Empty {storage}")                             
