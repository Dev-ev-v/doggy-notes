from dataclasses import dataclass, field

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.value_objects.criterion import Criterion


@dataclass(frozen=True)
class NoteSelector:
    ids: list[str] = field(default_factory=list)
    tags: list[Criterion] = field(default_factory=list)
    titles: list[Criterion] = field(default_factory=list)
    mode: Mode = Mode.AND

    def __post_init__(self) -> None:
        filled = [bool(self.ids), bool(self.tags), bool(self.titles)]
        if sum(filled) > 1:
            raise ValueError(
                "Only one selection method can be used: "
                "ids, tags or titles."
            )

    @property
    def is_empty(self) -> bool:
        return not self.ids and not self.tags and not self.titles