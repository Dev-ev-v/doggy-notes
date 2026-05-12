from doggy_notes.domain.exceptions.note_errors import *

class NoteService:

    def __init__(self, repo):
        self.repo = repo

    def save_service(self, note):
        if note.title:
            if len(note.title) > 120:
                raise ValueError("Title too long")
        self.repo.save(note)

    def get_service(
        self,
        id: str | None = None,
        tags: list[str] | None = None
    ):
        if id and tags:
            raise ValueError("Use id or tags, not both")
        if id:
            if len(id) == 8:
                return self.repo.get_by_short_id(id)
            return self.repo.get_by_id(id)
        elif tags:
            return [tag for tag in tags], [self.repo.get_by_tag(tag) for tag in tags]
        else:
            return self.repo.get_all()

    def delete_service(self, note):
        self.repo.delete(note)        