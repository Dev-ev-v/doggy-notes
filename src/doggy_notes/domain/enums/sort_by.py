from enum import Enum

class SortBy(str, Enum):
    created_at = "created_at"
    title = "title"