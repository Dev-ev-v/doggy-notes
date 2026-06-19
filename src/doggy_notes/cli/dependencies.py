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
from doggy_notes.presentation.presenters.file_presenter import FilePresenter
from doggy_notes.presentation.presenters.error_presenter import ErrorPresenter
from doggy_notes.presentation.formatters.date_formatter import DateFormatter

# === CLI ===
from doggy_notes.cli.parsers.tag_parser import TagParser
from doggy_notes.cli.parsers.id_parser import IDParser
from doggy_notes.cli.console import Console
from doggy_notes.cli.help_messages import HelpMessages

class CommandDependencies(NamedTuple):
    service: NoteService
    console: Console
    tag_parser: TagParser
    id_parser: IDParser
    note_presenter: NotePresenter
    error_presenter: ErrorPresenter
    file_presenter: FilePresenter
    date_formatter: DateFormatter
    help_messages: HelpMessages
    
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
    def tag_parser(self) -> TagParser:
        if not hasattr(self, '_tag_parser'):
            self._tag_parser = TagParser()
        return self._tag_parser
        
    @property
    def id_parser(self) -> IDParser:
        if not hasattr(self, '_id_parser'):
            self._id_parser = IDParser()
        return self._id_parser
    
    @property
    def note_presenter(self) -> NotePresenter:
        if not hasattr(self, '_note_presenter'):
            self._note_presenter = NotePresenter()
        return self._note_presenter
        
    @property
    def error_presenter(self) -> ErrorPresenter:
        if not hasattr(self, '_error_presenter'):
            self._error_presenter = ErrorPresenter()
        return self._error_presenter
    
    @property
    def file_presenter(self) -> FilePresenter:
        if not hasattr(self, '_file_presenter'):
            self._file_presenter = FilePresenter()
        return self._file_presenter                
    
    @property
    def date_formatter(self) -> DateFormatter:
        if not hasattr(self, '_date_formatter'):
            self._date_formatter = DateFormatter()
        return self._date_formatter
        
    @property
    def help_messages(self) -> HelpMessages:
        if not hasattr(self, '_help_messages'):
            self._help_messages = HelpMessages()
        return self._help_messages
    
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
            tag_parser=self.tag_parser,
            id_parser=self.id_parser,
            note_presenter=self.note_presenter,
            error_presenter=self.error_presenter,
            file_presenter=self.file_presenter,
            date_formatter=self.date_formatter,
            help_messages=self.help_messages,
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
