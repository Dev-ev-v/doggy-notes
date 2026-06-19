class IDParserConfig:
    id_filter = "[]() "
    	    
class IDParser:    
    @staticmethod
    def parse_id(raw_id: str) -> str:
        if not raw_id:
            return ""
        return raw_id.strip(IDParserConfig.id_filter)


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