from enum import Enum
from typing import Dict, Any, Optional


class ErrorCode(str, Enum):
    NOTE_ERROR = "NOTE_ERROR"
    NOTE_NOT_FOUND = "NOTE_NOT_FOUND"
    NOTE_VALIDATION_ERROR = "NOTE_VALIDATION_ERROR"
    SEARCH_FILTER_ERROR = "SEARCH_FILTER_ERROR"
    STORAGE_EMPTY = "STORAGE_EMPTY"
    NOTE_OPERATION_ERROR = "NOTE_OPERATION_ERROR"
    NOTE_IMPORTATION_ERROR = "NOTE_IMPORTATION_ERROR"
    NOTE_EXPORTATION_ERROR = "NOTE_EXPORTATION_ERROR"
    PATH_NOT_FOUND_ERROR = "PATH_NOT_FOUND_ERROR"
    NOTE_AMBIGUOUS_ID_ERROR = "NOTE_AMBIGUOUS_ID_ERROR"


class AppError(Exception):

    def __init__(self, message: str, code: ErrorCode, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.context: Dict[str, Any] = context or {}
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"[{self.code.value}] {self.message} ({context_str})"
        return f"[{self.code.value}] {self.message}"

    def __str__(self) -> str:
        return self._format_message()

NoteException = AppError


class NoteNotFoundError(AppError):
    def __init__(self, filters: Dict[str, Any], message: str = None):
        super().__init__(
            message or "No notes found with the applied filters",
            code=ErrorCode.NOTE_NOT_FOUND,
            context={"filters": filters},
        )


class NoteValidationError(AppError):
    def __init__(self, field: str = "", message: str = ""):
        msg = f"Failed validation in '{field}': {message}" if field else message
        super().__init__(
            msg,
            code=ErrorCode.NOTE_VALIDATION_ERROR,
            context={"field": field} if field else None,
        )


class SearchFilterError(AppError):
    def __init__(self, filter: str = None, value: str = None, message: str = ""):
        super().__init__(
            message or f"Invalid filter {filter}",
            code=ErrorCode.SEARCH_FILTER_ERROR,
            context={"filter": filter, "value": value},
        )


class NoteEmptyStorageError(AppError):
    def __init__(self, message: str = None):
        super().__init__(
            message or "Notes storage empty",
            code=ErrorCode.STORAGE_EMPTY,
        )


class NoteOperationError(AppError):
    def __init__(self, operation: str = "", message: str = ""):
        super().__init__(
            message or f"Error during operation: {operation}",
            code=ErrorCode.NOTE_OPERATION_ERROR,
            context={"operation": operation} if operation else None,
        )


class NoteImportationError(AppError):
    def __init__(self, message: str = ""):
        super().__init__(
            message or "Cannot complete note importation",
            code=ErrorCode.NOTE_IMPORTATION_ERROR,
        )


class NoteExportError(AppError):
    def __init__(self, message: str = ""):
        super().__init__(
            message or "Cannot complete note exportation",
            code=ErrorCode.NOTE_EXPORTATION_ERROR,
        )


class PathNotFoundError(AppError):
    def __init__(self, path: str):
        super().__init__(
            f"Path '{path}' does not exist",
            code=ErrorCode.PATH_NOT_FOUND_ERROR,
            context={"path": path},
        )


class NoteAmbiguousIDError(AppError):
    def __init__(self, short_id: str, count: int):
        super().__init__(
            f"Short ID '{short_id}' matches {count} notes, use the full ID",
            code=ErrorCode.NOTE_AMBIGUOUS_ID_ERROR,
            context={"short_id": short_id, "count": count},
        )