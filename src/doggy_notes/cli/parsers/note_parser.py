import re
import unicodedata 
from doggy_notes.domain.exceptions.note_errors import InvalidNoteError

class NoteParser:

    @staticmethod
    def parse_id(raw_input: str) -> str:
        return re.sub(r'^[\[\]()\s]+|[\[\]()\s]+$', '', raw_input)

    @staticmethod 
    def parse_tags(tags: list[str]) -> list[str]:
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