from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError
from doggy_notes.domain.enums.mode import Mode

class ByTags:
	def matches(self, selector) -> bool:
		return bool(selector.tags)

	def fetch(self, repo, selector, trash: bool) -> QueryResult:
		includes = [c.value for c in selector.tags if not c.exclude]
		excludes = [c.value for c in selector.tags if c.exclude]
        
		groups = {}
		result = repo.get_by_tags(includes, excludes, selector.mode, trash)

		if selector.mode == Mode.OR:
			for note in result:
				for tag in note.tags:
					if tag in includes:
						groups.setdefault(tag, []).append(note)

		elif selector.mode == Mode.AND:
			groups[", ".join(includes)] = result

		items = list({note.id: note for note in result}.values())

		return QueryResult(
			items=items,
			groups=groups,
			filters={"tags": includes, "excluded_tags": excludes},
		)

	def not_found_error(self, selector, trash: bool) -> NoteNotFoundError:
		includes = [c.value for c in selector.tags if not c.exclude]
		return NoteNotFoundError({"tags": includes})