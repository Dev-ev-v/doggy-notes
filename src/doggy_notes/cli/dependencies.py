from pathlib import Path

from doggy_notes.infra.serializer import NoteSerializer
from doggy_notes.infra.storage import NoteStorage
from doggy_notes.json.repository import NoteRepository
from doggy_notes.application.service import NoteService
from doggy_notes.cli.presenters import NotePrintMessages


def get_service():
    directory = Path.home() / "doggy-notes"
    directory.mkdir(parents=True, exist_ok=True)

    repo = NoteRepository(
        NoteStorage(),
        NoteSerializer(),
        directory
    )

    return NoteService(repo)


def get_printer():
    return NotePrintMessages()