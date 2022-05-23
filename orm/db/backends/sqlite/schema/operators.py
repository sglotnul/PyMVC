from abc import abstractmethod
from mymvc2.orm.db.operator import Operator
from mymvc2.orm.db.backends.mysql.schema.operators import field_to_sql
from mymvc2.orm.db.entries import DataEngine

class SQliteDeleteTableOperation(Operator):
	CMD = "DROP TABLE {};"

	def __init__(self):
		self._cols = []

	def set(self, table: str):
		self._cols.append(table)

	def to_str(self) -> str:
		separator = "\n"
		return separator.join(self.CMD.format(table) for table in self._cols)

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQLiteAlterTableOperator(Operator):
	@abstractmethod
	def mutate_disposer_state(self):
		raise NotImplementedError()

class SQliteAddOperator(SQLiteAlterTableOperator):
	CMD = "ALTER TABLE {table} ADD {column};"

	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = {}

	def set(self, col: str, meta: dict):
		self._cols[col] = meta
	
	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for col, meta in self._cols.items():
			if state.get(col):
				raise Exception("column already exists")
			state[col] = meta

	def to_str(self) -> str:
		separator = "\n"

		return separator.join(self.CMD.format(
			table = self._disposer.get_table_name(), 
			column = field_to_sql(field, meta['data_type'], meta['default'], meta['null'])
		) for field, meta in self._cols.items())

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQLiteDropOperator(SQLiteAlterTableOperator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = []

	def set(self, col: str):
		self._cols.append(col)

	def _field_to_sql(self, field: str, meta: dict) -> str:
		data_type = meta["data_type"]
		return f"{field} {data_type}"
	
	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for col in self._cols:
			try:
				del state[col]
			except: 
				raise Exception("unable to drop nonexistent column")

	def to_str(self) -> str:
		disposer = self._disposer

		table_name = disposer.get_table_name()
		backup_table_name = table_name + "_backup"

		backup_fields = disposer.get_state()

		separator = "\n"

		return separator.join((
			disposer.get_schema().create_table(backup_table_name, backup_fields).to_str(),
			DataEngine().insert(backup_table_name).insert_from(table_name, tuple(backup_fields.keys())).to_str(),
			disposer.get_schema().delete_table(table_name).to_str(),
			disposer.__class__(disposer.get_schema(), backup_table_name, backup_fields).rename_to(table_name).to_str(),
		))

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQliteAddForeignKeyOperator(SQLiteDropOperator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = {}

	def set(self, col: str, table: str):
		self._cols[col] = table

	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for col, table in self._cols.items():
			if not state.get(col):
				raise Exception("unable to add foreign key to nonexistent column")
			state[col]['references'] = table
	
class SQliteRenameOperator(SQLiteAlterTableOperator):
	CMD = "ALTER TABLE {} RENAME TO {};"

	def __init__(self, disposer: object):
		self._name = None
		self._disposer = disposer

	def set(self, name: str):
		self._name = name

	def mutate_disposer_state(self):
		pass
	
	def to_str(self) -> str:
		return self.CMD.format(self._disposer.get_table_name(), self._name)

	def __bool__(self) -> bool:
		return bool(self._name)


