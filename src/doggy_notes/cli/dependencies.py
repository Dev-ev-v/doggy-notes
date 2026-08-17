from functools import lru_cache, cached_property
from typing import NamedTuple

# === Infra ===
from doggy_notes.infra.paths import build_paths
from doggy_notes.infra.persistence.sqlite_note_repository import SQLiteNoteRepository

# === Domain ===
from doggy_notes.domain.config import NoteConfig
from doggy_notes.domain.repositories.note_repository import NoteRepository

# === Application (use_cases) ===
from doggy_notes.application.use_cases.create_note import CreateNoteUseCase
from doggy_notes.application.use_cases.read_notes import ReadNotesUseCase
from doggy_notes.application.use_cases.delete_notes import DeleteNotesUseCase
from doggy_notes.application.use_cases.edit_note import EditNoteUseCase
from doggy_notes.application.use_cases.list_notes import ListNotesUseCase
from doggy_notes.application.use_cases.legacy_importer import LegacyImporterUseCase
from doggy_notes.application.use_cases.export_notes import ExportNotesUseCase
from doggy_notes.application.use_cases.trash_notes import TrashNotesUseCase

# === Application (others) ===
from doggy_notes.application.builders.selection import Selector
from doggy_notes.application.services.note_resolver import NoteResolver
from doggy_notes.application.services.editor_service import EditorService
from doggy_notes.application.services.note_service import NoteService

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
from doggy_notes.cli.parsers.criterion_parser import CriterionParser


class CommandDependencies(NamedTuple):
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
    legacy_importer: LegacyImporterUseCase
    export_notes: ExportNotesUseCase
    trash_notes: TrashNotesUseCase
    selector: Selector
    resolver: NoteResolver


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

        self._initialized = True

    # ===== Infra =====

    @cached_property
    def paths(self):
        return build_paths()

    @cached_property
    def repository(self) -> NoteRepository:
        return SQLiteNoteRepository(self.paths.database_file, self.note_config)

    # ===== Domain =====

    @cached_property
    def note_config(self) -> NoteConfig:
        return NoteConfig()

    # ===== CLI =====

    @cached_property
    def console(self) -> Console:
        return Console()

    @cached_property
    def criterion_parser(self) -> CriterionParser:
    	return CriterionParser()
    	
    @cached_property
    def tag_parser(self) -> TagParser:
        return TagParser(self.criterion_parser)

    @cached_property
    def id_parser(self) -> IDParser:
        return IDParser(self.note_config)

    @cached_property
    def note_presenter(self) -> NotePresenter:
        return NotePresenter(self.note_config)

    @cached_property
    def error_presenter(self) -> ErrorPresenter:
        return ErrorPresenter()

    @cached_property
    def file_presenter(self) -> FilePresenter:
        return FilePresenter()

    @cached_property
    def date_formatter(self) -> DateFormatter:
        return DateFormatter()

    @cached_property
    def help_messages(self) -> HelpMessages:
        return HelpMessages()

    # ===== Application =====

    @cached_property
    def service(self) -> NoteService:
        return NoteService(self.repository, self.note_config)

    @cached_property
    def editor(self) -> EditorService:
        return EditorService()
    
    @cached_property
    def resolver(self) -> NoteResolver:
    	return NoteResolver(self.repository)
    
    @cached_property
    def create_note(self) -> CreateNoteUseCase:
        return CreateNoteUseCase(self.service, self.editor)

    @cached_property
    def read_notes(self) -> ReadNotesUseCase:
        return ReadNotesUseCase(self.service, self.resolver)

    @cached_property
    def delete_notes(self) -> DeleteNotesUseCase:
        return DeleteNotesUseCase(self.service, self.resolver)

    @cached_property
    def edit_note(self) -> EditNoteUseCase:
        return EditNoteUseCase(self.service, self.resolver, self.editor)

    @cached_property
    def list_notes(self) -> ListNotesUseCase:
        return ListNotesUseCase(self.service, self.resolver)

    @cached_property
    def legacy_importer(self) -> LegacyImporterUseCase:
        return LegacyImporterUseCase(self.service, self.tag_parser, self.id_parser, self.create_note)

    @cached_property
    def export_notes(self) -> ExportNotesUseCase:
        return ExportNotesUseCase(self.service, self.resolver)
        
    @cached_property
    def trash_notes(self) -> TrashNotesUseCase:
    	return TrashNotesUseCase(self.service, self.resolver)
    	
    @cached_property
    def selector(self) -> Selector:
    	return Selector(self.id_parser, self.tag_parser, self.criterion_parser)

    def get_command_dependencies(self) -> CommandDependencies:

        return CommandDependencies(
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
            legacy_importer=self.legacy_importer,
            export_notes=self.export_notes,
            trash_notes=self.trash_notes,
            selector=self.selector,
            resolver=self.resolver,
        )


def get_container() -> DIContainer:
    return DIContainer()


def get_dependencies() -> CommandDependencies:
    return get_container().get_command_dependencies()