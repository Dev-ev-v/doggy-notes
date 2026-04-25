import json
from pathlib import Path

BASE_DIR = Path.home() / ".meu_app"
BASE_DIR.mkdir(exist_ok=True)

def list_notes():
    return sorted(BASE_DIR.glob(f"*.json"))

def save_note(data: dict, filename: str, content: str) -> Path:
    file_name = f"{filename}.json"
    file_path = BASE_DIR / file_name
    if isinstance(content, str):
    	path = Path(content)
    if path.exists() and path.is_file():
        data["content"] = path.read_text(encoding="utf-8")
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path

def load_note(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def unsave_note(index: int | None, delete_all: bool) -> None:
    if delete_all:
        for f in list_notes():
            f.unlink()
        return    
    else:
    	file = list_notes()[index - 1]     
    	file.unlink()