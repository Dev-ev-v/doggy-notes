from functools import lru_cache
from doggy_notes.infra.paths import build_paths
from doggy_notes.infra.database.migrations import ensure_schema
from doggy_notes.infra.persistence.sqlite_note_repository import SQLiteNoteRepository
from doggy_notes.domain.services.note_service import NoteService

@lru_cache
def get_paths():
    return build_paths()

@lru_cache
def get_repository():
    paths = get_paths()
    return SQLiteNoteRepository(paths.database_file)

@lru_cache
def get_service():
    return NoteService(get_repository())
    
def initialize_database() -> None:
    paths = get_paths()
    ensure_schema(paths.database_file)