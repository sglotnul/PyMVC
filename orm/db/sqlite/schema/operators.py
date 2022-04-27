from mymvc2.orm.db.operator import Operator
from mymvc2.orm.db.schema.operators import RenameOperator, AlterTableOperator, field_to_sql
from mymvc2.orm.db.entries import DataEngine

class SQliteDeleteTableOperation(Operator):
	CMD = "DROP TABLE %(table)s;"

	def __init__(self):
		self._cols = []

	def set(self, table: str):
		self._cols.append(table)

	def __str__(self) -> str:
		separator = "\n"
		return separator.join((self.CMD % {
			'table': table,
		} for table in self._cols))

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQliteAddOperator(AlterTableOperator):
	CMD = "ADD %(column)s"

	def __init__(self, disposer: object):
		super().__init__(disposer.get_table_state_name())
		self._disposer = disposer
		self._cols = {}

	def set(self, col: str, meta: dict):
		self._cols[col] = meta
	
	def _mutate_disposer_state(self):
		state = self._disposer.get_state()
		for col, meta in self._cols.items():
			if state.get(col):
				raise Exception("")
			state[col] = meta

	def __str__(self) -> str:
		self._mutate_disposer_state()

		cmd = ""
		separator = "\n"

		for field, meta in self._cols.items():
			operation = self.CMD % {
				'column': field_to_sql(field, meta['data_type'], meta['default'], meta['null']),
			} 
			cmd += separator + self.ALTER_TABLE % {
				'table': self._table,
				'operation': operation
			}

		return cmd

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQLiteDropOperator(Operator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = []

	def set(self, col: str):
		self._cols.append(col)

	def _field_to_sql(self, field: str, meta: dict) -> str:
		data_type = meta["data_type"]
		return f"{field} {data_type}"
	
	def _mutate_disposer_state(self) -> dict:
		state = self._disposer.get_state()
		for col in self._cols:
			try:
				del state[col]
			except: 
				raise Exception("")
		return state

	def __str__(self) -> str:
		self._mutate_disposer_state()

		disposer = self._disposer

		table_name = disposer.get_table_state_name()
		backup_table_name = table_name + "_backup"

		backup_fields = disposer.get_state()

		schema = disposer.get_schema()
		backup_table_schema = schema.alter_table(backup_table_name, backup_fields)
		data_engine = DataEngine()

		postfix = "\n"

		command_tuple = (
			schema.create_table(backup_table_name, backup_fields, instantly=True),
			data_engine.insert_from(backup_table_name, table_name, tuple(backup_fields.keys())),
			schema.delete_table(table_name, instantly=True),
			backup_table_schema.rename_to(table_name, instantly=True)
		)

		return postfix.join(command_tuple)

	def __bool__(self) -> bool:
		return bool(self._cols)

class SQliteAddForeignKeyOperator(SQLiteDropOperator):
	def __init__(self, disposer: object):
		self._disposer = disposer
		self._cols = {}

	def set(self, col: str, table: str):
		self._cols[col] = table

	def _mutate_disposer_state(self) -> dict:
		state = self._disposer.get_state()
		for col, table in self._cols.items():
			if not state.get(col):
				raise Exception("")
			state[col]['references'] = table
		return state
	
class SQliteRenameOperator(RenameOperator):
	def __init__(self, disposer: object):
		super().__init__(disposer.get_table_state_name())
		self._disposer = disposer

	def _mutate_disposer_state(self) -> dict:
		self._disposer.set_table_state_name(self._name)
	
	def _create_operation_body(self) -> str:
		self._mutate_disposer_state()

		return super()._create_operation_body()