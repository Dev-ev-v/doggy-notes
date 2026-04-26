from doggy_notes.domain.note import Note

class NotePrintMessages:
    def print_notes(self, notes: list["Note"] | None):
        if not notes:
            print("No notes found")
            return

        for i, note in enumerate(notes, 1):
            print(f"\n[{i}] {note.name}\nContent: {note.content[:150]}")

    def get_confirmation(self, files: list["Note"] | None):
        if not files:
            print("Invalid notes!")
            return False

        print("Are you sure you want to delete these notes?\n")
        self.print_notes(files)

        answer = input("\n[y/n]: ")

        if answer.lower() == "y":
            if len(files) > 1:
            	print("Notes successfully deleted")
            else:
            	print("Note successfully deleted")	
            return True
        print("Operation aborted")
        return False