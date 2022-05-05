import sqlite3
from mymvc2.orm.db.executor import BaseExecutor
from mymvc2.orm.db.sqlite.schema import SQLiteSchemaEngine

class SQLiteExecutor(BaseExecutor):
	schema_engine = SQLiteSchemaEngine

	def __init__(self, executor):
		self._executor = executor
		self._cursor = executor.cursor()

	@classmethod
	def connect(cls, path: str):
		executor = sqlite3.connect(path)
		return cls(executor)

	def fetch(self):
		return self._cursor.fetchall()

	def commit(self) -> int:
		self._executor.commit()

	def close(self):
		self._executor.close()

	def rollback(self):
		self._executor.rollback()

	def get_lastrowid(self) -> int:
		return self._cursor.lastrowid

	def _prepare_query(self, query: str) -> str:
		return "BEGIN;\n" + query

	def __call__(self, query: str, *, script=False):
		if not query:
			return
		execute = self._cursor.execute
		if script:
			query = self._prepare_query(query)
			execute = self._cursor.executescript
		try:
			execute(query)
			self.commit()
		except self._executor.Error as err:
			if script:
				self.rollback()
			raise err