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
    def get_by_id(self, note_id: str) -> list[Note]:
        pass
    
    @abstractmethod
    def get_by_short_id(self, note_id: str) -> list[Note]:
    	pass
    
    @abstractmethod
    def get_by_tag(self, tag: str) -> list[Note]:
    	pass		

    @abstractmethod
    def get_all(self) -> list[Note]:
        pass

    @abstractmethod
    def delete(self, note: Note) -> None:
        pass