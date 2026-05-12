from pathlib import Path

from doggy_notes.infra.storage import NoteStorage
from doggy_notes.domain.services.note_service import NoteService
from doggy_notes.cli.controller import NoteCLI
from doggy_notes.infra.presenters.note_presenter import NotePresenter
from doggy_notes.infra.persistence.sqlite_note_repository import SQLiteNoteRepository
from doggy_notes.domain.repositories.note_repository import NoteRepository

def get_service():
    repo = SQLiteNoteRepository(NoteStorage().resolve("doggy-notes.db"))
    return NoteService(repo)

def get_printer():
    return NoteCLI(NotePresenter)