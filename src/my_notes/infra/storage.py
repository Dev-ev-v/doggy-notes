from pathlib import Path

class NoteStorage:
    def write(self, path: Path, data: dict):
    	path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    	
    def delete(self, file: Path):
    	file.unlink()
    
    def list(self, base_dir: Path, type: str):
    	return sorted(base_dir.glob(type))
    	
    def read(self, path: Path):
    	return path.read_text(encoding="utf-8")