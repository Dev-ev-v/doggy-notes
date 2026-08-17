from doggy_notes.domain.value_objects.criterion import Criterion

class CriterionParser:
    
    def parse(self, raw: str) -> Criterion:
    	exclude = raw.startswith("!")
    	value = raw[1:] if exclude else raw
    	return Criterion(value=value, exclude=exclude)