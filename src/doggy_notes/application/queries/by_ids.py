from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError
from .flatten_groups import flatten_groups
from doggy_notes.domain.config import NoteConfig

class ByIds:
	
	def matches(self, selector) -> bool:
		return bool(selector.ids)

	def fetch(self, repo, selector, trash: bool) -> QueryResult:
		groups = {
			id: self._fetch_by_id(repo, id, trash)
			for id in selector.ids
		}
		items = flatten_groups(groups)
		return QueryResult(
			items=items,
			groups=groups,
			filters={"ids": selector.ids},
		)

	def not_found_error(self, selector, trash: bool) -> NoteNotFoundError:
		return NoteNotFoundError({"ids": selector.ids})
		
	def _fetch_by_id(self, repo, id: str, trash: bool):
		is_short_id = len(id) == NoteConfig().short_id_length
		result = (
			repo.get_by_short_id(id, trash)
			if is_short_id
			else repo.get_by_id(id, trash)
		)
		return result if isinstance(result, list) else [result] if result else []