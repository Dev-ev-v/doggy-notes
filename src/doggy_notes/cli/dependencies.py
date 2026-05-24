from functools import lru_cache
from typing import NamedTuple

# === Infra ===
from doggy_notes.infra.paths import build_paths
from doggy_notes.infra.database.schema import ensure_schema
from doggy_notes.infra.persistence.sqlite_note_repository import SQLiteNoteRepository

# === Domain ===
from doggy_notes.domain.services.note_service import NoteService

# === Application (Use Cases) ===
from doggy_notes.application.use_cases.create_note import CreateNoteUseCase
from doggy_notes.application.use_cases.read_notes import ReadNotesUseCase
from doggy_notes.application.use_cases.delete_notes import DeleteNotesUseCase
from doggy_notes.application.use_cases.edit_note import EditNoteUseCase
from doggy_notes.application.use_cases.list_notes import ListNotesUseCase

# === Presentation ===
from doggy_notes.presentation.presenters.note_presenter import NotePresenter
from doggy_notes.presentation.formatters.date_formatter import DateFormatter

# === CLI ===
from doggy_notes.cli.console import Console
from doggy_notes.cli.parsers.note_parser import NoteParser

class CommandDependencies(NamedTuple):
    service: NoteService
    console: Console
    parser: NoteParser
    presenter: NotePresenter
    
    create_note: CreateNoteUseCase
    read_notes: ReadNotesUseCase
    delete_notes: DeleteNotesUseCase
    edit_note: EditNoteUseCase
    list_notes: ListNotesUseCase

class DIContainer:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
   
        self._paths = build_paths()
        self._initialized = True
    
    # ===== Infra =====
    
    @property
    @lru_cache(maxsize=1)
    def paths(self):
        return self._paths
    
    @property
    def repository(self) -> SQLiteNoteRepository:
        if not hasattr(self, '_repository'):
            self._repository = SQLiteNoteRepository(self.paths.database_file)
        return self._repository
    
    # ===== Domain =====
    
    @property
    def service(self) -> NoteService:
        if not hasattr(self, '_service'):
            self._service = NoteService(self.repository)
        return self._service
    
    # ===== Presentation =====
    
    @property
    def console(self) -> Console:
        if not hasattr(self, '_console'):
            self._console = Console()
        return self._console
    
    @property
    def parser(self) -> NoteParser:
        if not hasattr(self, '_parser'):
            self._parser = NoteParser()
        return self._parser
    
    @property
    def presenter(self) -> NotePresenter:
        if not hasattr(self, '_presenter'):
            self._presenter = NotePresenter()
        return self._presenter
    
    @property
    def date_formatter(self) -> DateFormatter:
        if not hasattr(self, '_date_formatter'):
            self._date_formatter = DateFormatter()
        return self._date_formatter
    
    # ===== Use Cases =====
    
    @property
    def create_note(self) -> CreateNoteUseCase:
        if not hasattr(self, '_create_note'):
            self._create_note = CreateNoteUseCase(self.service)
        return self._create_note
    
    @property
    def read_notes(self) -> ReadNotesUseCase:
        if not hasattr(self, '_read_notes'):
            self._read_notes = ReadNotesUseCase(self.service)
        return self._read_notes
    
    @property
    def delete_notes(self) -> DeleteNotesUseCase:
        if not hasattr(self, '_delete_notes'):
            self._delete_notes = DeleteNotesUseCase(self.service)
        return self._delete_notes
    
    @property
    def edit_note(self) -> EditNoteUseCase:
        if not hasattr(self, '_edit_note'):
            self._edit_note = EditNoteUseCase(self.service)
        return self._edit_note
    
    @property
    def list_notes(self) -> ListNotesUseCase:
        if not hasattr(self, '_list_notes'):
            self._list_notes = ListNotesUseCase(self.service)
        return self._list_notes
    
    
    def get_command_dependencies(self) -> CommandDependencies:
    
        return CommandDependencies(
            service=self.service,
            console=self.console,
            parser=self.parser,
            presenter=self.presenter,
            create_note=self.create_note,
            read_notes=self.read_notes,
            delete_notes=self.delete_notes,
            edit_note=self.edit_note,
            list_notes=self.list_notes,
        )

    
    def initialize_database(self) -> None:
        ensure_schema(self.paths.database_file)
    
    def shutdown(self) -> None:
        if hasattr(self, '_repository'):
            self._repository.close()
            

def get_container() -> DIContainer:
    return DIContainer()


def get_dependencies() -> CommandDependencies:
    return get_container().get_command_dependencies()
