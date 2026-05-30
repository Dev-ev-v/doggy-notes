import re
import unicodedata 
from doggy_notes.domain.exceptions.note_errors import NoteException

class NoteParser:

    @staticmethod
    def parse_id(id: str) -> str:
        if not id:
        	return ""
        return re.sub(r'^[\[\]()\s]+|[\[\]()\s]+$', '', id)
    
    @staticmethod
    def parse_ids(ids: list[str]) -> list[str]:
    	if not ids:
    		return []
    	normalized_ids = []
    	seen = set()
    	for id in ids:
    		if not id in seen:
    			id = NoteParser.parse_id(id)
    			seen.add(id)
    			normalized_ids.append(id)
    	return normalized_ids

    @staticmethod 
    def parse_tags(tags: list[str]) -> list[str]:
        if not tags:
        	return []
        normalized_tags = []
        seen = set()
        for raw_tag in tags:
            tag = raw_tag.strip()
            if not tag:
                continue
            tag = unicodedata.normalize("NFC", tag)
            if any(ord(char) < 32 or ord(char) == 127 for char in tag):
                raise InvalidNoteError(
                    tag,
                    "Tag contains invalid control characters",
                )
            lowered = tag.casefold()
            if lowered not in seen:
                seen.add(lowered)
                normalized_tags.append(tag)
        return normalized_tags