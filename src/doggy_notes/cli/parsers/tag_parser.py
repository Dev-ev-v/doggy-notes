import re
import unicodedata

from doggy_notes.domain.exceptions.note_errors import SearchFilterError

class TagParserConfig:
    tag_filter = r'[\w \-+.#/]+'


class TagParser:


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

            tag = TagParser._sanitize_escape_literals(tag)
            tag = unicodedata.normalize("NFC", tag)
            
            TagParser._get_invalid_chars(tag)

            lowered = tag.casefold()
            if lowered not in seen:
                seen.add(lowered)
                normalized_tags.append(tag)
        return normalized_tags

    
    @staticmethod
    def _get_invalid_chars(tag: str) -> SearchFilterError | None:

        invalid_characters = list({
            repr(char) for char in tag
            if not re.fullmatch(TagParserConfig.tag_filter, char)
        })

        if invalid_characters:
            raise SearchFilterError("Tag contains invalid characters", tag, " ".join(invalid_characters))
            
    
    @staticmethod
    def _sanitize_escape_literals(tag: str) -> str:
    	return re.sub(r'\\[ntr\\]', '', tag)