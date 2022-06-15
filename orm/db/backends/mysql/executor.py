from pafmvc.orm.db.executor import BaseExecutor
from .schema import MySqlSchemaEngine

class SQLiteExecutor(BaseExecutor):
	schema_engine = MySqlSchemaEngine

	def __init__(self, path: str):
		self._executor = None

	def commit(self) -> int:
		self._executor.commit()

	def close(self):
		self._executor.close()

	def rollback(self):
		self._executor.rollback()

	def get_lastrowid(self) -> int:
		return self._executor.lastrowid

	def __call__(self, query: str, *, script=False):
		pass