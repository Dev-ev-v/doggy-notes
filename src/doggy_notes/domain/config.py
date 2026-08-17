from dataclasses import dataclass

@dataclass(frozen=True)
class NoteConfig:
    max_title_length: int = 100
    id_length: int = 32
    short_id_length: int = 8