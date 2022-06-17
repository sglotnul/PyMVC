from importlib import import_module
from pafmvc.conf import settings

def connect(path="", db_path="") -> object:
	executor = getattr(import_module(path or settings.DB_EDITOR_PATH), settings.DB_EDITOR)
	return executor(db_path or settings.DB_PATH)