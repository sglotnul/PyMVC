from concurrent.futures import Executor
from importlib import import_module as default_import
from mymvc2.conf import settings

def connect(path="", db_path="") -> object:
	executor = getattr(default_import(path or settings.DB_EDITOR_PATH), settings.DB_EDITOR)
	return executor(db_path or settings.DB_PATH)
