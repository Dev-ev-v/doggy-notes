from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.exceptions.note_errors import NoteNotFoundError


class ByTitles:

    def matches(self, selector) -> bool:
        return bool(selector.titles)

    def fetch(self, repo, selector, trash: bool) -> QueryResult:
        includes = [c.value for c in selector.titles if not c.exclude]
        excludes = [c.value for c in selector.titles if c.exclude]

        items = repo.get_by_titles(includes, excludes, trash)

        groups = {}
        for title in includes:
            groups[title] = [n for n in items if title.lower() in n.title.lower()]

        return QueryResult(
            items=items,
            groups=groups,
            filters={"titles": includes, "excluded_titles": excludes},
        )

    def not_found_error(self, selector, trash: bool) -> NoteNotFoundError:
        includes = [c.value for c in selector.titles if not c.exclude]
        return NoteNotFoundError({"titles": includes})