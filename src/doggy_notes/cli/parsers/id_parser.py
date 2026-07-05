import re
import logging
import uuid

logger = logging.getLogger(__name__)

class IDParserConfig:
    id_filter = "[]() "
    	    
class IDParser:    
    @staticmethod
    def parse_id(raw_id: str) -> str:        	
        if not raw_id:
            return ""
        
        normalized_id = raw_id.strip(IDParserConfig.id_filter)
        
        is_id = IDParser._is_uuid4_hex(normalized_id)
        
        if is_id:
        	return normalized_id
        
        else:
        	return ""


    @staticmethod
    def parse_ids(ids: list[str]) -> list[str]:
        if not ids:
            return []
        
        normalized_ids = []
        seen = set()
        
        for raw_id in ids:
            normalized_id = IDParser.parse_id(raw_id)

            if normalized_id not in seen:
                seen.add(normalized_id)
                normalized_ids.append(normalized_id)
        return normalized_ids
        
    
    @staticmethod
    def _is_uuid4_hex(s: str) -> bool:
    	return bool(
    		re.fullmatch(r'[0-9a-f]{8}', s) or
    		re.fullmatch(r'[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}', s)
    	)