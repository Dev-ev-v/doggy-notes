from abc import ABC, abstractmethod
from doggy_notes.domain.entities.note import Note


class NoteRepository(ABC):

    @abstractmethod
    def create(self, note: Note) -> None:
        pass

    @abstractmethod
    def update(self, note: Note) -> None:
        pass

    @abstractmethod
    def get_by_id(self, note_id: str, trash: bool) -> Note | None:
        pass

    @abstractmethod
    def get_by_short_id(self, short_id: str, trash: bool) -> Note | None:
        pass

    @abstractmethod
    def get_by_tags(self, tags: list[str], mode: str, trash: bool) -> list[Note]:
        pass

    @abstractmethod
    def get_all(self, trash: bool) -> list[Note]:
        pass

    @abstractmethod
    def add_to_trash(self, note: Note) -> None:
        pass

    @abstractmethod
    def restore_from_trash(self, note: Note) -> None:
        pass

    @abstractmethod
    def delete(self, note: Note) -> None:
        pass

    @abstractmethod
    def exists_by_id(self, id: str) -> bool:
        pass

    @abstractmethod
    def exists_by_fingerprint(self, fingerprint: str) -> str | None:
        pass