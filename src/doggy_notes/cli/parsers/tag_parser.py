import re
import unicodedata

from doggy_notes.domain.exceptions.note_errors import SearchFilterError
from doggy_notes.domain.value_objects.criterion import Criterion

class TagParserConfig:
    tag_filter = r'[\w \-+.#/]+'


class TagParser:

    def __init__(self, criterion_parser):
        self.criterion_parser = criterion_parser
        self.config = TagParserConfig

    def parse_tags(self, tags: list[str]) -> list[Criterion]:
        if not tags:
            return []
        normalized_criteria = []
        seen = set()

        for raw_tag in tags:
            criterion = self.criterion_parser.parse(raw_tag.strip())

            tag = criterion.value.strip()
            if not tag:
                continue

            tag = self._sanitize_escape_literals(tag)
            tag = unicodedata.normalize("NFC", tag)

            self._get_invalid_chars(tag)

            lowered = tag.casefold()
            key = (lowered, criterion.exclude)
            if key not in seen:
                seen.add(key)
                normalized_criteria.append(Criterion(value=tag, exclude=criterion.exclude))

        return normalized_criteria

    def _get_invalid_chars(self, tag: str) -> None:
        invalid_characters = list({
            repr(char) for char in tag
            if not re.fullmatch(self.config.tag_filter, char)
        })

        if invalid_characters:
            raise SearchFilterError(
                filter=tag,
                value=" ".join(invalid_characters),
                message="Tag contains invalid characters",
            )

    def _sanitize_escape_literals(self, tag: str) -> str:
        return re.sub(r'\\[ntr\\]', '', tag)