import argparse
from pathlib import Path
from my_notes.infra.serializer import NoteSerializer
from my_notes.infra.storage import NoteStorage
from my_notes.json.repository import NoteRepository
from my_notes.application.service import NoteService
from my_notes.cli.presenters import NotePrintMessages
from my_notes.domain.note import Note
from datetime import datetime

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
    delete_parser.add_argument("index", nargs="*", type=int)
    delete_parser.add_argument("--all", action="store_true")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("term")

    args = parser.parse_args()
    
    directory = Path.home() / 'notes'
    directory.mkdir(parents=True, exist_ok=True)
    repo = NoteRepository(NoteStorage(), NoteSerializer(), directory)
    service = NoteService(repo)
    print_system = NotePrintMessages()

    if args.command == "add":
        note = Note(
        content=args.content,
        title=args.title,
        description=args.description,
        tags=args.tags,
        date=datetime.now())
        
        service.create_note(note)

    elif args.command == "list":
        notes = service.get_all_notes()
        print_system.print_notes(notes)

    elif args.command == "delete":
        files = service.get_note_by_index(args.index, args.all)
        can_delete = print_system.get_confirmation(files)
        if can_delete:
        	service.delete_note(files)
   
    else:
        parser.print_help()

if __name__ == "__main__":
    main()