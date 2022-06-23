from pafmvc.orm.db.executor import BaseExecutor
from .schema import MySqlSchemaEngine

class SQLiteExecutor(BaseExecutor):
	schema_engine = MySqlSchemaEngine

	def connect(self):
		pass

	def commit(self) -> int:
		pass

	def close(self):
		pass

	def rollback(self):
		pass

	def __call__(self, query: str, *, script=False):
		pass