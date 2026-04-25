import argparse
from my_notes.core.services import create_note, get_all_notes, delete_note, search_note

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

    if args.command == "add":
        create_note(args.content, args.title, args.description, args.tags)

    elif args.command == "list":
        notes = get_all_notes()
        for i, note in enumerate(notes, 1):
            print(f"{i}. {note}")

    elif args.command == "delete":
        if not args.all:
        	if args.index is None or index <= 0:
        		print("Indice inválido")
        		return    
        delete_note(args.index, args.all)

    elif args.command == "search":
        results = search_note(args.term)
        if results:
        	print(f"Resultados encontrados: {results}")
        else:	
        	print("Nenhum resultado foi encontrado")
   
    else:
        parser.print_help()

if __name__ == "__main__":
    main()