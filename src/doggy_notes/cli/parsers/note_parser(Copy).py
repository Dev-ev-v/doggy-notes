import re
import unicodedata

from doggy_notes.domain.exceptions.note_errors import SearchFilterError

class NoteParserConfig:
    id_filter = "[]() "
    tag_filter = r'[\w \-+.#/]+'


class NoteParser:

    @staticmethod
    def parse_id(raw_id: str) -> str:
        if not raw_id:
            return ""
        return raw_id.strip(NoteParserConfig.id_filter)


    @staticmethod
    def parse_ids(ids: list[str]) -> list[str]:
        if not ids:
            return []
        normalized_ids = []
        seen = set()
        for raw_id in ids:
            normalized_id = NoteParser.parse_id(raw_id)

            if normalized_id not in seen:
                seen.add(normalized_id)
                normalized_ids.append(normalized_id)
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

            tag = NoteParser._sanitize_escape_literals(tag)
            tag = unicodedata.normalize("NFC", tag)
            
            NoteParser._get_invalid_chars(tag)

            lowered = tag.casefold()
            if lowered not in seen:
                seen.add(lowered)
                normalized_tags.append(tag)
        return normalized_tags

    
    @staticmethod
    def _get_invalid_chars(tag: str) -> SearchFilterError:

        invalid_characters = list({
            repr(char) for char in tag
            if not re.fullmatch(NoteParserConfig.tag_filter, char)
        })

        if invalid_characters:
            raise SearchFilterError("Tag contains invalid characters", tag, " ".join(invalid_characters))
            
    @staticmethod
    def _sanitize_escape_literals(tag: str) -> str:
    	return re.sub(r'\\[ntr\\]', '', tag)