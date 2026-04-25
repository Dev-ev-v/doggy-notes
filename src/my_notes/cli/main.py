import argparse
from pathlib import Path
from my_notes.src.my_notes.json.repository import NoteRepository
from my_notes.src.my_notes.application.service import NoteService
from my_notes.src.my_notes.infra.serializer import NoteSerializer
from my_notes.src.my_notes.infra.storage import NoteStorage
from my_notes.src.my_notes.domain.note import Note

def main():
    parser = argparse.ArgumentParser(description="CLI de notas")

    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--title", default=None)
    add_parser.add_argument("--description", default=None)
    add_parser.add_argument("content")
    add_parser.add_argument("--tags", nargs="*")

    subparsers.add_parser("list")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("index", nargs="?", type=int)
    delete_parser.add_argument("--all", action="store_true")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("term")

    args = parser.parse_args()
    
    repo = NoteRepository(Path.home() / "notes", NoteSerializer, NoteStorage)
    repo.mkdir(exist_ok=True)
    service = NoteService(repo)

    if args.command == "add":
        note = Note(
        content=args.content,
        title=args.title,
        description=args.description,
        tags=args.tags,
        timestamp=datetime.now())
        
        create_note(note)

    elif args.command == "list":
        notes = get_all_notes()
        for i, note in enumerate(notes, 1):
            print(f"{i}. {note}")

    elif args.command == "delete":
        delete_note(args.index, args.all)
   
    else:
        parser.print_help()

if __name__ == "__main__":
    main()