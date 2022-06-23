from ast import If
import sqlite3
from pafmvc.orm.db.executor import BaseExecutor
from .schema import SQLiteSchemaEngine

def connect_only(func):
	def wrapper(self, *args, **kwargs):
		if not hasattr(self, "_executor"):
			raise Exception("executor isn't connected")
		return func(self, *args, **kwargs)
	return wrapper

class SQLiteExecutor(BaseExecutor):
	schema_engine = SQLiteSchemaEngine

	def connect(self):
		if getattr(self, '_executor', None):
			self._executor.close()
		self._executor = sqlite3.connect(self._path)
	
	@connect_only
	def close(self):
		self._executor.close()

	@connect_only
	def commit(self) -> int:
		self._executor.commit()

	@connect_only
	def rollback(self):
		self._executor.rollback()

	def _prepare_query(self, query: str) -> str:
		return "BEGIN;\n" + query

	@connect_only
	def __call__(self, query: str, *, script=False) -> sqlite3.Cursor:
		if not query:
			return
		try:
			cur = self._executor.executescript(self._prepare_query(query)) if script else self._executor.execute(query)
			self.commit()
			return cur
		except self._executor.Error as err:
			if script:
				self.rollback()
			raise err