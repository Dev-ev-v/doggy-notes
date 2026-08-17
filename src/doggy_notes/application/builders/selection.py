import typer
from typing import List, Optional

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.value_objects.criterion import Criterion
from doggy_notes.domain.value_objects.note_selector import NoteSelector


class Selector:

	def __init__(self, id_parser, tag_parser, criterion_parser):
		self.id_parser = id_parser
		self.tag_parser = tag_parser
		self.criterion_parser = criterion_parser
	
	def build_selector(
		self,
		ids: Optional[List[str]] = None,
		tags: Optional[List[str]] = None,
		titles: Optional[List[str]] = None,
		mode: Mode = Mode.AND,
	) -> NoteSelector:
	    
	    return NoteSelector(
	    	ids=self.id_parser.parse_ids(ids) if ids else [],
	    	tags=self.tag_parser.parse_tags(tags) if tags else [],
	    	titles=[self.criterion_parser.parse(t) for t in titles] if titles else [],
	    	mode=mode,
	    )