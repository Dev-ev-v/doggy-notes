import logging
from pathlib import Path
from datetime import datetime, timezone
import json

from doggy_notes.domain.exceptions.note_errors import PathNotFoundError, NoteExportError
from doggy_notes.application.mappers.note_export_mapper import NoteExportMapper
from doggy_notes.infra.paths import build_paths
from doggy_notes.presentation.formatters.date_formatter import DateFormatter
from doggy_notes.domain.enums.file_format import ExportFileFormat


logger = logging.getLogger(__name__)


class ExportNotesUseCase:

    def __init__(self, service):
        self.service = service
        self.mapper = NoteExportMapper
        self.formatter = DateFormatter

    def resolve_output_path(self, output_path: Path | None = None) -> Path:

        if not output_path:
            logger.debug("No path provided, exporting in exports_dir")
            output_path = build_paths().exports_dir

        if not output_path.exists():
            raise PathNotFoundError(output_path)

        return output_path

    def resolve_notes(
        self,
        ids: list[str] | None = None,
        tags: list[str] | None = None,
        mode: str = "AND",
    ):
        result = self.service.get(
            ids=ids,
            tags=tags,
            mode=mode,
        )

        return result

    def execute(self, result, output_path=None, suffix: ExportFileFormat = ExportFileFormat.json):

        export_time = datetime.now(timezone.utc)

        output_file = output_path / f"export_{self.formatter.to_filename(export_time)}{suffix.extension}"

        if suffix == ExportFileFormat.json:
            self.to_json(result, output_file)

        elif suffix == ExportFileFormat.markdown:
            parts = [self.to_markdown(note) for note in result.items]
            output_file.write_text("\n\n---\n\n".join(parts), encoding="utf-8")

        elif suffix == ExportFileFormat.txt:
            parts = [self.to_txt(note) for note in result.items]
            output_file.write_text("\n\n---\n\n".join(parts), encoding="utf-8")

        else:
            raise NoteExportError(f"Unsupported export format: {suffix}")

        return output_file

    def to_json(self, result, output_file: Path):
        data = {
            "notes": [self.mapper.to_dict(note) for note in result.items]
        }

        output_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def to_markdown(self, note) -> str:
        parts = [f"# {note.title}"] if note.title else ["# Untitled"]

        if note.description:
            parts.append(f"\n## {note.description}")

        parts.append(f"\nID: {note.id}")
        parts.append(f"\nCreated_at: {note.created_at}")

        parts.append(f"\n{note.content}")

        if note.tags:
            parts.append("\n**Tags:** " + ", ".join(note.tags))

        return "\n".join(parts)

    def to_txt(self, note) -> str:
        parts = [note.title] if note.title else ["Untitled"]

        if note.description:
            parts.append(note.description)

        parts.append(f"ID: {note.id}")
        parts.append(f"Created_at: {note.created_at}")
        parts.append("-" * 40)

        parts.append(note.content)

        if note.tags:
            parts.append("Tags: " + ", ".join(note.tags))

        return "\n".join(parts)