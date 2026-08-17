from doggy_notes.application.queries.strategies import QueryStrategy
from doggy_notes.application.queries.by_ids import ByIds
from doggy_notes.application.queries.by_tags import ByTags
from doggy_notes.application.queries.by_titles import ByTitles
from doggy_notes.application.queries.all_notes import AllNotes


class NoteResolver:

    STRATEGIES: list[QueryStrategy] = [
    	ByIds(), 
    	ByTags(),
    	ByTitles(),
    	AllNotes()
    ]

    def __init__(self, repo):
        self.repo = repo

    def resolve(self, selector, trash=False):
        strategy = next(
            s for s in self.STRATEGIES
            if s.matches(selector)
        )

        result = strategy.fetch(
            self.repo,
            selector,
            trash,
        )

        if result.is_empty:
            raise strategy.not_found_error(selector, trash)

        return result                        