from enum import Enum

class ImportFileFormat(str, Enum):
	json = "json"
	markdown = "md"
	
	@property
	def extension(self) -> str:
		return f".{self.value}"
		
	@classmethod
	def _missing_(cls, value):
	    if isinstance(value, str):
	        normalized = value.strip().lower().lstrip(".")
	        for member in cls:
	            if member.value == normalized:
	            	return member
	    return None

	
class ExportFileFormat(str, Enum):
	json = "json"
	markdown = "md"
	txt = "txt"
	
	@property
	def extension(self) -> str:
		return f".{self.value}"
		
	@classmethod
	def _missing_(cls, value):
	    if isinstance(value, str):
	        normalized = value.strip().lower().lstrip(".")
	        for member in cls:
	            if member.value == normalized:
	            	return member
	    return None				