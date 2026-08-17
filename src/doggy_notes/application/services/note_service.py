import logging
from typing import Optional, Protocol

from doggy_notes.domain.enums.mode import Mode
from doggy_notes.domain.config import NoteConfig


logger = logging.getLogger(__name__)

class NoteService:

	def __init__(self, repo, config: Optional[NoteConfig] = None):
		self.repo = repo
		self.config = config or NoteConfig()

	
	def validate_note(self, note, verify_id: bool = True, verify_fingerprint = True):
		
		valid = True
		messages = []

		if verify_id:
			valid_id, msg = self._validate_id(note)
			if not valid_id:
				valid = False
				messages.append(msg)

		valid_title, msg = self._validate_title(note)
		if not valid_title:
			valid = False
			messages.append(msg)

		if verify_fingerprint:
			valid_fingerprint, msg = self._validate_fingerprint(note)
			if not valid_fingerprint:
				valid = False
				messages.append(msg)

		valid_content, msg = self._validate_content(note)
		if not valid_content:
			valid = False
			messages.append(msg)

		return valid, messages

	
	def create(self, note):
		success, messages = self.validate_note(note)
		if success:
			self.repo.create(note)
		return success, messages

	
	def update(self, note):
		success, msg = self.validate_note(note, False, False)
		if success:
			self.repo.update(note)
		return success, msg
		
	
	def delete(self, note):
		self.repo.delete(note)

	
	def add_to_trash(self, note):
		self.repo.add_to_trash(note)
		
	
	def restore_from_trash(self, note):
		self.repo.restore_from_trash(note)

	
	def _validate_id(self, note):
		
		errors = []
		if self.repo.exists_by_id(note.id):
			logger.debug("Skipping note %s: ID already exists", note.id[:self.config.short_id_length])
			errors.append(f"ID {note.id[:self.config.short_id_length]} already exists")
			
		if len(note.id) != self.config.id_length:
			errors.append(f"ID length must be of {self.config.id_length}, not {len(note.id)}")
			
		if errors:
			return False, ', '.join(errors)		

		return True, None

	
	def _validate_fingerprint(self, note):
		
		if self.repo.exists_by_fingerprint(note.fingerprint):
			logger.debug("Skipping note %s: duplicate content (fingerprint match)", note.id[:self.config.short_id_length])
			return False, f"Note {note.id[:self.config.short_id_length]} has duplicate content of an existing note"
	       
		return True, None

	
	def _validate_title(self, note):
		title = note.title.strip()
		logger.debug("Note not saved: note without title")
		if not title:
			return False, f"Note {note.id[:self.config.short_id_length]} without title"
			
		if len(title) > self.config.max_title_length:
			logger.debug("Skipping note %s: title exceds limit of %s", note.id[:self.config.short_id_length], str(self.config.max_title_length))
			return False, f"Note {note.id[:self.config.short_id_length]} has a too long title"

		return True, None

	
	def _validate_content(self, note):
		content = note.content.strip()
		if not content:
			logger.debug("Note %s not saved: no provided content", note.id)
			return False, f"Note {note.id[:self.config.short_id_length]} with empty content"

		return True, None