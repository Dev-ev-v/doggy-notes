from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from rich.text import Text

@dataclass
class ErrorDetail:
    code: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"[{self.code}] {self.message} ({context_str})"
        return f"[{self.code}] {self.message}"


class NoteException(Exception):
    
    def __init__(self, message: str = "", code: str = "NOTE_ERROR"):
        self.message = message
        self.code = code
        self.errors: List[ErrorDetail] = []
        
        if message:
            self.add_error(code, message)
        
        super().__init__(self._format_message())
    
    def add_error(self, code: str, message: str, context: Optional[Dict[str, Any]] = None) -> "NoteException":        
        error = ErrorDetail(code=code, message=message, context=context or {})
        self.errors.append(error)
        return self
    
    def add_errors(self, errors: List[tuple]) -> "NoteException":     
        for error_data in errors:
            if len(error_data) == 3:
                code, message, context = error_data
                self.add_error(code, message, context)
            else:
                code, message = error_data
                self.add_error(code, message)
        return self
    
    def has_errors(self) -> bool:        
        return len(self.errors) > 0
    
    def error_count(self) -> int:      
        return len(self.errors)
    
    def _format_message(self) -> str:
        if not self.errors:
            return self.message or "Unknown error"
        
        if len(self.errors) == 1:
            return str(self.errors[0])
        
        error_lines = [f"Many errors found ({len(self.errors)}):"]
        for i, error in enumerate(self.errors, 1):
            error_lines.append(f"  {i}. {error}")
        
        return "\n".join(error_lines)
    
    def __str__(self) -> str:
        return self._format_message()
    
    def get_errors(self) -> List[ErrorDetail]:
        return self.errors
    
    def get_error_codes(self) -> List[str]:
        return [error.code for error in self.errors]


class NoteNotFoundError(NoteException):
    def __init__(self, filters: Dict[str, Any], message: str = None):
        self.filters = filters
        msg = message or "No notes found with the applied filters"
        super().__init__(msg, code="NOTE_NOT_FOUND")


class NoteValidationError(NoteException):
   
    def __init__(self, field: str = "", message: str = "", validation_errors: List[tuple] = None):
        self.field = field
        
        if validation_errors:
            msg = f"Note(s) validation error"
            super().__init__(msg, code="NOTE_VALIDATION_ERROR")
            self.add_errors(validation_errors)
        else:
            msg = f"Failed validation in '{field}': {message}" if field else message
            super().__init__(msg, code="NOTE_VALIDATION_ERROR")


class SearchFilterError(NoteException):
    
    def __init__(self, message: str = "", filter: str = None, value: str = None):
        super().__init__(message or f"Invalid filter {filter}", code="SEARCH_FILTER_ERROR")
        self.filter = filter
        self.value = value


class NoteEmptyStorageError(NoteException):
    
    def __init__(self, message: str = None):
        msg = message or "Notes storage empty"
        super().__init__(msg, code="STORAGE_EMPTY")


class NoteOperationError(NoteException):
    
    def __init__(self, operation: str = "", message: str = "", errors: List[tuple] = None):
        msg = message or f"Error during operation: {operation}"
        super().__init__(msg, code="NOTE_OPERATION_ERROR")
        
        if errors:
            self.add_errors(errors)                                                                                