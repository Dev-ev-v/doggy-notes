import logging
from dataclasses import dataclass
from typing import Optional

from doggy_notes.domain.exceptions.note_errors import SearchFilterError, NoteNotFoundError, NoteEmptyStorageError
from doggy_notes.application.dto.query_result import QueryResult
from doggy_notes.domain.enums.mode import Mode


logger = logging.getLogger(__name__)

@dataclass
class NoteServiceConfig:
    max_title_length: int = 100
    short_id_length: int = 8


class NoteService:
    def __init__(self, repo, config: Optional[NoteServiceConfig] = None):
        self.repo = repo
        self.config = config or NoteServiceConfig()
        
    
    def validate_note(self, note, verify_id: bool = True):

        valid_title, msg = self._validate_title(note)
        if not valid_title:
            return False, msg
                    
        if verify_id:
        	valid_id, msg = self._validate_id(note)
        	if not valid_id:
        		return False, msg
        
        valid_fingerprint, msg = self._validate_fingerprint(note)        
        if not valid_fingerprint:
        	return False, msg
        
        return True, None

    
    def create(self, note):
    	success, msg = self.validate_note(note)
    	if success:
    		self.repo.create(note)
    	return success, msg

    
    def update(self, note):
        success, msg = self.validate_note(note, False)
        if success:
        	self.repo.update(note)
        return success, msg

    
    def delete(self, note):
        self.repo.delete(note)

    
    def get(
        self,
        ids: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        mode: Mode = Mode.AND,
    ) -> QueryResult:

        if ids:
            result = self._get_by_ids(ids)

        if tags:
            result = self._get_by_tags(tags, mode)

        if not ids and not tags:
            result = self._get_all()

        self._is_empty(result, ids, tags)

        return result
        
    
    def _validate_fingerprint(self, note):
    	existing_id = self.repo._exists_by_fingerprint(note.fingerprint)
    	
    	if existing_id:
    		logger.debug("Note %s already exist in storage", note.id[:8])
    	
    	return True, None
    
    
    def _validate_id(self, note):
    	if self.repo._exists_by_id(note.id):
    		logger.debug("Skipping note %s: ID already exists", note.id[:8])
    		return False, None
    	
    	return True, None
    	
    	
    def _validate_title(self, note):
    	if len(note.title) > self.config.max_title_length:
    		logger.debug("Skipping note %s: title exceds limit of %s", note.id[:8], str(self.config.max_title_length))
    		return False, None
    	
    	return True, None

    
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

    
    def _get_by_tags(self, tags: list[str], mode: str) -> QueryResult:
        groups = {}
        result = self.repo.get_by_tags(tags, mode)

        if mode == "OR":
            
            for note in result:
            	for tag in note.tags:
            		if tag in tags:
            			groups.setdefault(tag, []).append(note)

        elif mode == "AND":
            groups[", ".join(tags)] = result

        items = list({note.id: note for note in result}.values())

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

    
    def _is_empty(self, result, ids, tags):
        if result.is_empty:
            if tags:
                filters = {}
                filters["tags"] = tags
                raise NoteNotFoundError(filters)
            elif ids:
                filters = {}
                filters["ids"] = ids
                raise NoteNotFoundError(filters)
            raise NoteEmptyStorageError("Empty storage, create a note first")