import shutil
import logging
from platformdirs import user_data_dir
from pathlib import Path


logger = logging.getLogger(__name__)

APP_NAME = "doggy-notes"

data_dir = Path(user_data_dir(APP_NAME))

NO_FUNCTIONAL_PATHS = [
	Path(data_dir / "exports"),
]

def clean_no_functional_paths():
    
    for path in NO_FUNCTIONAL_PATHS:
    	if path.exists():
    		logger.info("Deleting no functional path %s", path)
    		children = path.iterdir()
    		
    		for child in children:
    			logger.debug("%s from %s is being deleted", child, path)
    			
    		shutil.rmtree(path)
    		logger.info("%s succesfully deleted", path)
    		