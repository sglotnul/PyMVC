from mymvc2.orm.db.schema import SchemaEngine, TableSchemaEngine
from mymvc2.orm.db.backends.mysql.schema.operators import CreateTableOperator, ChangeTableOperator
from .operators import *
from mymvc2.orm.db.schema import operator_delegating_metod

class SQLiteTableSchemaEngine(TableSchemaEngine):
	def __init__(self, schema: object, table: str, fields: dict):
		super().__init__(table, fields)
		self._schema = schema
	
	@operator_delegating_metod
	def alter(self, col: str, field_meta: dict):
		self.drop(col)
		self.add(col, field_meta)
		
	def get_table_name(self) -> str:
		return self._table

	def get_state(self) -> dict:
		return self._state
	
	def get_schema(self) -> object:
		return self._schema.__class__()
	
	def reset(self):
		self._state = self._fields
		self._operators['drop'] = SQLiteDropOperator(self)
		self._operators['add'] = SQliteAddOperator(self)
		self._operators['add_fk'] = SQliteAddForeignKeyOperator(self)
		self._operators['rename_to'] = SQliteRenameOperator(self)
	
	def to_str(self) -> str:
		separator = "\n"
		applied_operators = []
		for operator in self._operators.values():
			if operator:
				operator.mutate_disposer_state()
				applied_operators.append(operator.to_str())
		return separator.join(applied_operators)

class SQLiteSchemaEngine(SchemaEngine):
	def alter_table(self, table: str, fields: dict) -> SQLiteTableSchemaEngine:
		table_schema_engine = SQLiteTableSchemaEngine(self, table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine

	def reset(self):
		self._operators['delete_table'] = SQliteDeleteTableOperation()
		self._operators['create_table'] = CreateTableOperator()
		self._operators['alter_table'] = ChangeTableOperator()