from abc import abstractmethod
from pafmvc.orm.db.operator import Operator
from pafmvc.orm.db.entries import DataEngine
from pafmvc.orm.db.schema import FieldSchema

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
		self._cols = []

	def set(self, field: FieldSchema):
		self._cols.append(field)
	
	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for field in self._cols:
			if state.get(field.name, None) is not None:
				raise Exception("column already exists")
			state[field.name] = field

	def _add_single_field(self, field: FieldSchema) -> str:
		return self.CMD.format(
			table = self._disposer.get_table_name(), 
			column = field.to_sql(),
		)

	def to_str(self) -> str:
		separator = "\n"
		return separator.join(self._add_single_field(field) for field in self._cols)

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQLiteDropOperator(SQLiteAlterTableOperator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = []

	def set(self, field: str):
		self._cols.append(field)

	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for field in self._cols:
			try:
				del state[field]
			except KeyError: 
				raise Exception("unable to drop nonexistent column")

	def to_str(self) -> str:
		disposer = self._disposer

		table_name = disposer.get_table_name()
		backup_table_name = table_name + "_backup"

		backup_fields = disposer.get_state()

		separator = "\n"

		schema = disposer.get_schema()
		query = schema.create_table(backup_table_name, backup_fields.values()).to_str() + separator
		schema = disposer.get_schema()
		query += DataEngine().insert(backup_table_name).insert_from(table_name, tuple(backup_fields.keys())).to_str() + separator
		query += schema.delete_table(table_name, disposer.fields).to_str() + separator
		schema = disposer.get_schema()
		query += schema.alter_table(backup_table_name, backup_fields.values()).rename_to(table_name).to_str()

		return query

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQliteAddForeignKeyOperator(SQLiteDropOperator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = []

	def set(self, field: FieldSchema):
		self._cols.append(field)

	def mutate_disposer_state(self):
		state = self._disposer.get_state()
		for field in self._cols:
			state[field.name] = field
	
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