from my_notes.domain.note import Note

class NotePrintMessages:
    def print_notes(self, notes: list["Note"] | None):
        if not notes:
            print("Nenhuma nota encontrada.")
            return

        for i, note in enumerate(notes, 1):
            print(f"\n[{i}] {note.name}\nContent: {note.content[:100]}")

    def get_confirmation(self, files: list["Note"] | None):
        if not files:
            print("Informe uma nota válida!")
            return False

        print("Você deseja mesmo apagar os seguintes itens?\n")
        self.print_notes(files)

        answer = input("\n[y/n]: ")

        if answer.lower() == "y":
            print("Nota/notas deletada/deletadas com sucesso")
            return True
        print("Operação cancelada")
        return False