import logging
import shutil
from pathlib import Path
import json
from datetime import datetime, timezone

from doggy_notes.domain.exceptions.note_errors import NoteImportationError
from doggy_notes.domain.dto.skipped_note import SkippedNoteData
from doggy_notes.infra.paths import build_paths
from doggy_notes.application.validation.type_checker import validate_fields
from doggy_notes.domain.entities.note import Note, generate_id


logger = logging.getLogger(__name__)

SUPPORTED_DATE_FORMATS = (
    "%Y-%m-%d_%H-%M-%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
)

VALID_FORMATS = (
    ".json",
    ".md",
)

OLD_FIELDS = (
    "time",
    "date",
)

FIELDS_TO_REMOVE = (
    "fingerprint",
)

REQUIRED_FIELDS = (
    "content",
    "id",
)

OLD_DATA_DIRS = (
    Path.home() / ".meu_app",
    Path.home() / "notes",
    Path.home() / "doggy-notes",
)

# Markdown note separator, must match ExportNotesUseCase.execute()
MARKDOWN_NOTE_SEPARATOR = "\n\n---\n\n"


class LegacyImporterUseCase:
    
    def __init__(self, service, tag_parser, id_parser, create_note):
        self.service = service
        self.tag_parser = tag_parser
        self.id_parser = id_parser
        self.create_note = create_note

    
    def import_notes_from_old_dirs(self):
        legacy_dirs = []

        for dir in OLD_DATA_DIRS:
            children = list(dir.glob("*.json"))
            if children:
                legacy_dirs.append(dir)

        if not legacy_dirs:
            logger.debug("No legacy notes found. Skipping JSON import.")
            return

        imported_files = []

        for legacy_dir in legacy_dirs:
            for json_file in legacy_dir.glob("*.json"):
                try:
                    saved_notes, _, _ = self.import_file(json_file)
                    if saved_notes:
                    	imported_files.append(json_file)
                except Exception:
                    logger.exception("Failed to import %s", json_file)

        logger.debug("%s files imported", imported_files)

        archive_failed = []

        for json_file in imported_files:
            try:
                self._archive_file(json_file)
            except Exception:
                logger.exception("Failed to archive %s", json_file)
                archive_failed.append(json_file)

        if archive_failed:
            logger.warning(
                "%d file(s) could not be archived: %s",
                len(archive_failed),
                [f.name for f in archive_failed]
            )

    
    def _archive_file(self, json_file: Path) -> None:

        archive_dir = json_file.parent / "archived"
        backup_dir = json_file.parent / "backup"

        archive_dir.mkdir(exist_ok=True)
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / json_file.name
        archived_path = archive_dir / json_file.name

        shutil.copy2(json_file, backup_path)

        shutil.move(
            str(json_file),
            str(archived_path)
        )

        logger.info(
            "Archived legacy file: %s",
            json_file.name
        )

    
    def resolve_output_path(self, output_path: Path | None = None) -> Path:

        if not output_path:
            logger.debug("No path provided, importing from last export in exports_dir")
            output_path = build_paths().exports_dir

        if not output_path.exists():
            raise NoteImportationError("Selected path does not exist")

        return output_path

    
    def valid_file(self, file: Path) -> bool:
        valid_format = file.suffix in VALID_FORMATS

        if file.suffix == ".json":
            try:
                json.loads(file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise NoteImportationError(
                    f"'{file.name}' Is not a valid json file: the file may be corrupted or broken"
                ) from e

        return valid_format

    
    def import_file(self, file: Path) -> tuple[list, list, list]:
        logger.info("Importing notes from %s", file.name)
        parser = self._get_parser(file.suffix)
        raw_notes = parser(file)

        saved_notes, skipped_datas, errors = [], [], []

        for note_data in raw_notes:
            result, success, error_msg = self._save_note(note_data)
            (saved_notes if success else skipped_datas).append(result)
            if error_msg:
                errors.append(error_msg)

        logger.info(
            "%s file import complete: %d notes saved, %d notes skipped, %d errors",
            file.name, len(saved_notes), len(skipped_datas), len(errors)
        )

        return saved_notes, errors, skipped_datas

    
    def _get_parser(self, suffix: str):
        parsers = {
            ".json": self._parse_json,
            ".md": self._parse_markdown,
        }
        parser = parsers.get(suffix)

        if not parser:
            raise NoteImportationError(f"Unsupported file format: {suffix}")

        return parser

    
    def _parse_json(self, file: Path) -> list[dict]:
        data = json.loads(file.read_text(encoding="utf-8"))

        if isinstance(data, dict) and data.get("notes"):
            return data["notes"]

        return [data]

    
    def _parse_markdown(self, file: Path) -> list[dict]:
        """
        Parses .md files produced by ExportNotesUseCase.to_markdown().
        A single export file may contain several notes, joined by
        MARKDOWN_NOTE_SEPARATOR, so we split on that first.
        """
        content = file.read_text(encoding="utf-8").strip()

        if not content:
            return []

        blocks = content.split(MARKDOWN_NOTE_SEPARATOR)
        return [self._parse_markdown_block(block) for block in blocks]

    
    def _parse_markdown_block(self, block: str) -> dict:
        lines = block.strip("\n").split("\n")
        note_data: dict = {}
        content_lines = []

        title = None
        description = None
        idx = 0

        # First line is the title, written as "# Title"
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            idx = 1

        for line in lines[idx:]:
            stripped = line.strip()

            if stripped.startswith("## ") and description is None:
                description = stripped[3:].strip()
            elif stripped.startswith("ID:"):
                note_data["id"] = stripped[len("ID:"):].strip()
            elif stripped.startswith("Created_at:"):
                note_data["created_at"] = stripped[len("Created_at:"):].strip()
            elif stripped.startswith("**Tags:**"):
                tags_str = stripped[len("**Tags:**"):].strip()
                note_data["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
            else:
                content_lines.append(line)

        if title:
            note_data["title"] = title
        if description:
            note_data["description"] = description

        note_data["content"] = "\n".join(content_lines).strip()

        return note_data
        

    def clean(self, note_data: dict):
        note_data = self._remove_old_fields(note_data)
        note_data = self._remove_fields_to_remove(note_data)
        note_data = self._drop_none_fields(note_data)

        return note_data

    
    @staticmethod
    def _parse_timestamp(value: str) -> str:
        if not value:
            return ""

        try:
            dt = datetime.fromisoformat(value)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt.isoformat()

        except ValueError:
            pass

        for fmt in SUPPORTED_DATE_FORMATS:
            try:
                dt = datetime.strptime(value, fmt)
                dt = dt.replace(tzinfo=timezone.utc)

                return dt.isoformat()

            except ValueError:
                continue

        return ""

    
    def _save_note(self, original_note_data: dict):

        note_data = original_note_data.copy()

        note_data_creation = (
            note_data.get("created_at")
            or note_data.get("date")
            or note_data.get("time")
            or ""
        )

        timestamp = self._parse_timestamp(note_data_creation)

        if timestamp:
            note_data["created_at"] = datetime.fromisoformat(timestamp)
        else:
            note_data.pop("created_at", None)

        note_data = self.clean(note_data)

        note_data_id = note_data.get("id")
        if not note_data_id:
            logger.debug("Note with empty ID detected, generating new ID")
            note_data_id = generate_id()
            note_data["id"] = note_data_id
            logger.debug("New ID %s generated", note_data_id)

        normalized_id = self.id_parser.parse_id(note_data_id)

        missing = [f for f in REQUIRED_FIELDS if not note_data.get(f)]
        type_errors = validate_fields(note_data, Note)

        if missing or type_errors:
            reasons = []
            if missing:
                logger.debug(f"Missing {', '.join(missing)}")
                reasons.append(f"Missing {', '.join(missing)}")
            reasons.extend(type_errors)

            return (
                self._build_skip(original_note_data, timestamp, reasons),
                False,
                "; ".join(reasons)
            )

        tags = note_data.get("tags", [])
        normalized_tags = self.tag_parser.parse_tags(tags)

        note_data["tags"] = normalized_tags
        note_data["id"] = normalized_id

        note = self.create_note.generate_note(note_data)

        success, error_messages = self.create_note.execute(note)

        if not success:
            return self._build_skip(original_note_data, timestamp, error_messages), False, error_messages

        return note, success, error_messages

    
    def _build_skip(self, original_note_data: dict, timestamp: str, reason) -> SkippedNoteData:

        preview = original_note_data.get("title") or "Untitled"
        id = str(original_note_data.get("id")) or "No ID"
        reasons = reason if isinstance(reason, list) else [reason]

        return SkippedNoteData(
            preview=str(preview),
            short_id=id[:8],
            date=timestamp or None,
            errors=reasons,
        )

    
    def _get_latest_export(self, exports_dir: Path) -> Path | None:
        exports = list(exports_dir.glob("export_*.json"))

        if not exports:
            logger.warning("No exportations found in %s", exports_dir)
            return None

        return max(exports, key=lambda f: f.stem.removeprefix("export_"))

    
    def _remove_old_fields(self, note_data):
        for field in OLD_FIELDS:
            note_data.pop(field, None)

        return note_data

    
    def _remove_fields_to_remove(self, note_data):
        for field in FIELDS_TO_REMOVE:
            note_data.pop(field, None)

        return note_data

    
    def _drop_none_fields(self, note_data: dict) -> dict:
        return {k: v for k, v in note_data.items() if v is not None}