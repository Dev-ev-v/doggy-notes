from datetime import datetime, timezone
import json

from doggy_notes.application.mappers.note_export_mapper import NoteExportMapper
from doggy_notes.infra.paths import build_paths
from doggy_notes.presentation.formatters.date_formatter import DateFormatter


class ExportNotesUseCase:

    def __init__(self, service):
        self.service = service
        self.mapper = NoteExportMapper
        self.formatter = DateFormatter

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

    def execute(self, result, output_path=None):
        if output_path is None:
            output_path = build_paths().exports_dir

        data = {
            "notes": [self.mapper.to_dict(note) for note in result.items]
        }

        export_time = datetime.now(timezone.utc)

        output_file = output_path / f"export_{self.formatter.to_filename(export_time)}.json"
        output_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return output_file