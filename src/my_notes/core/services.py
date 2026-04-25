from my_notes.domain.note import save_note, list_notes, load_note, unsave_note
from datetime import datetime

def search_note(term: str):
    term = term.lower()
    results = []
    for file in list_notes():
        note = load_note(file)
        if any(term in str(value).lower() for value in note.values()):
            results.append(f"{file}\n")
    return results

def create_note(content: str, title=None, description=None, tags=None):
	now = datetime.now()
	timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
	data = {
    "title": title,
    "description": description,
    "content": content,
    "tags": tags or [],
    "time": timestamp
	}
	if not search_note(content):
	       filename = (title or f"note_{int(datetime.now().timestamp())}").replace(" ", "_")
	       return save_note(data, filename, content)

def get_all_notes():
    notes = []
    for file in list_notes():
        notes.append(load_note(file))
    return notes

def delete_note(index: int | None, delete_all: bool):
    return unsave_note(index, delete_all)
    