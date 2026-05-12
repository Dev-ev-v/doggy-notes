from doggy_notes.domain.entities.note import Note
from doggy_notes.infra.presenters.note_presenter import NotePresenter

class NoteCLI:

    def __init__(self, presenter: NotePresenter):
        self.presenter = presenter

    def print_notes(self, notes: list[Note] | None):
        if not notes:
            print("No notes found")
            return
        for line in self.presenter.format_many(notes):
            print(line)
    
    def print_creat_message(self, note: Note):
    	output = self.presenter.format(note)
    	print(f"{output} created successfully")

    def get_confirmation(self, notes: list[Note] | None) -> bool:
        if not notes:
            print("Invalid notes!")
            return False
        print("Are you sure you want to delete these notes?\n")
        self.print_notes(notes)
        answer = input("\n[y/n]: ").strip().lower()
        if answer == "y":
            print(
                "Notes successfully deleted"
                if len(notes) > 1
                else "Note successfully deleted"
            )
            return True
        print("Operation aborted")
        return False