import logging
from pathlib import Path
import json
from datetime import datetime, timezone

from doggy_notes.domain.exceptions.note_errors import NoteImportationError
from doggy_notes.domain.dto.skipped_note import SkippedNoteData
from doggy_notes.infra.paths import build_paths
from doggy_notes.application.validation.type_checker import validate_fields
from doggy_notes.domain.entities.note import Note


logger = logging.getLogger(__name__)

SUPPORTED_DATE_FORMATS = (
    "%Y-%m-%d_%H-%M-%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
)

VALID_FORMATS = (
    ".json",
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

class LegacyImporterUseCase:

    def __init__(self, service, tag_parser, id_parser, create_note):
        self.service = service
        self.tag_parser = tag_parser
        self.id_parser = id_parser
        self.create_note = create_note


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
        	  	f"'{file.name}' Is not a valid json file: the file may be corrupted or broaken"
        	  ) from e        
        
        return valid_format        
                	  

    def import_json_note(self, json_file: Path) -> list:
        logger.info(
            "Importing notes from %s",
            json_file.name
        )

        data = json.loads(json_file.read_text(encoding="utf-8"))

        skipped_datas = []
        saved_notes = []
        errors = []

        if data.get("notes"):
            for note_data in data["notes"]:
                result, success, error_msg = self._save_note(note_data)

                if success:
                    saved_notes.append(result)
                else:
                    skipped_datas.append(result)

                if error_msg:
                    errors.append(error_msg)

        else:
            result, success, error_msg = self._save_note(data)

            if success:
                saved_notes.append(result)
            else:
                skipped_datas.append(result)

            if error_msg:
                errors.append(error_msg)

        logger.info(
            "%s file import complete: %d notes saved, %d notes skipped, %d errors",
            json_file.name,
            len(saved_notes),
            len(skipped_datas),
            len(errors)
        )

        return saved_notes, errors, skipped_datas


    def clean(self, note_data: dict):
        note_data = self._remove_old_fields(note_data)
        note_data = self._remove_fields_to_remove(note_data)
        
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
        	note_data["created_at"] = timestamp
        else:
        	note_data.pop("created_at", None)
        	
        note_data = self.clean(note_data)
        
        missing = [f for f in REQUIRED_FIELDS if not note_data.get(f)]
        type_errors = validate_fields(note_data, Note)
        
        if missing or type_errors:
        	reasons = []
        	if missing:
        		reasons.append(f"Missing {', '.join(missing)}")
        	reasons.extend(type_errors)
        	
        	return (
            	self._build_skip(original_note_data, timestamp, reasons),
          	  False,
        	    "; ".join(reasons)
     	   )

        note_data_id = note_data.get("id")
        normalized_id = self.id_parser.parse_id(note_data_id)

        if not normalized_id:
            logger.warning(
                "Note %s not imported: Invalid ID format",
                original_note_data.get("id")
            )
            
            return (
                self._build_skip(original_note_data, timestamp, "Invalid ID format"),
                False,
                f"Note {original_note_data.get('id')} not imported: invalid ID format"
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
    	
    	preview = original_note_data.get("title") or original_note_data.get("content") or "Untitled"
    	id = str(original_note_data.get("id")) or "No ID"
    	reasons = reason if isinstance(reason, list) else [reason]
    	
    	return SkippedNoteData(
    	    preview=str(preview)[:30],
    	    short_id = id[:8],
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