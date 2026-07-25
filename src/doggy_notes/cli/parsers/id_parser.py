import re
import logging
import uuid

logger = logging.getLogger(__name__)

class IDParserConfig:
    id_filter = "[]() "
    	    
class IDParser:
    
    def __init__(self, note_config, id_parser_config=None):
    	self.note_config = note_config
    	self.id_parser_config = id_parser_config or IDParserConfig()
	      
    def parse_id(self, raw_id: str) -> str:        	
        if not raw_id:
            return ""
            
        raw_id = str(raw_id)
        
        normalized_id = raw_id.strip(self.id_parser_config.id_filter)
        
        is_id = self._is_uuid4_hex(normalized_id)
        
        if is_id:
        	return normalized_id
        
        else:
        	logger.debug("%s is not a uuid4 valid ID", normalized_id)
        	return normalized_id


    def parse_ids(self, ids: list[str]) -> list[str]:
        if not ids:
            return []
        
        normalized_ids = []
        seen = set()
        
        for raw_id in ids:
            normalized_id = self.parse_id(raw_id)

            if normalized_id not in seen:
                seen.add(normalized_id)
                normalized_ids.append(normalized_id)
        return normalized_ids
        
    
    def _is_uuid4_hex(self, s: str) -> bool:
    	return bool(
			re.fullmatch(rf'[0-9a-f]{{{self.note_config.short_id_length}}}', s) or
			re.fullmatch(r'[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}', s)
	)