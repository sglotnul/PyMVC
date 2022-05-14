import sqlite3
from mymvc2.orm.db.executor import BaseExecutor
from mymvc2.orm.db.sqlite.schema import SQLiteSchemaEngine

class SQLiteExecutor(BaseExecutor):
	schema_engine = SQLiteSchemaEngine

	def __init__(self, path: str):
		self._executor = sqlite3.connect(path)

	def commit(self) -> int:
		self._executor.commit()

	def close(self):
		self._executor.close()

	def rollback(self):
		self._executor.rollback()

	def get_lastrowid(self) -> int:
		return self._executor.lastrowid

	def _prepare_query(self, query: str) -> str:
		return "BEGIN;\n" + query

	def __call__(self, query: str, *, script=False) -> sqlite3.Cursor:
		if not query:
			return
		execute = self._executor.execute
		if script:
			query = self._prepare_query(query)
			execute = self._executor.executescript
		try:
			cur = execute(query)
			self.commit()
			return cur
		except self._executor.Error as err:
			if script:
				self.rollback()
			raise err