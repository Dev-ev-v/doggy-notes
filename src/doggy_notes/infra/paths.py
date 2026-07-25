from dataclasses import dataclass
from pathlib import Path
from platformdirs import (
    user_cache_dir,
    user_config_dir,
    user_data_dir,
)

APP_NAME = "doggy-notes"

def get_exports_dir():
	downloads = Path.home() / "Downloads"
	download = Path.home() / "Download"
	
	if downloads.exists():
		exports_dir = downloads	
	elif download.exists():
		exports_dir = download	
	else:
		exports_dir = Path.home() / APP_NAME / "exports"
	
	return exports_dir


@dataclass(frozen=True)
class Paths:
    config_dir: Path
    data_dir: Path
    cache_dir: Path
    backups_dir: Path
    exports_dir: Path

    config_file: Path
    database_file: Path
    log_file: Path

def build_paths() -> Paths:
    config_dir = Path(user_config_dir(APP_NAME))
    data_dir = Path(user_data_dir(APP_NAME))
    cache_dir = Path(user_cache_dir(APP_NAME))
    backups_dir = data_dir / "backups"
    exports_dir = get_exports_dir()
    
    for d in (config_dir, data_dir, cache_dir, backups_dir, exports_dir):
        d.mkdir(parents=True, exist_ok=True)
    
    return Paths(
        config_dir=config_dir,
        data_dir=data_dir,
        cache_dir=cache_dir,
        backups_dir=backups_dir,
        exports_dir=exports_dir,
        
        log_file=cache_dir / "doggy_notes.log",
        config_file=config_dir / "config.toml",
   	 database_file=data_dir / "doggy_notes.db",
	)