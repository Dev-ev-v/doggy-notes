from enum import Enum

class NoteField(str, Enum):
    content = "content"
    title = "title"
    description = "description"
    tags = "tags"