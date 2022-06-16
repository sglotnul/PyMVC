from typing import Iterable
from pafmvc.orm.db.backends.mysql.schema import MySQLFieldSchema, MySQLForeignKeySchema, MySQLPrimaryKeySchema
from pafmvc.orm.db.backends.mysql.schema.operators import CreateTableOperator, ChangeTableOperator
from pafmvc.orm.db.schema import *
from .operators import *

class SQLiteTableSchemaEngine(TableSchemaEngine):
	def __init__(self, schema: SchemaEngine, table: str, fields: Iterable[FieldSchema]):
		super().__init__(schema, table, fields)
		self._state = dict((f.name, f) for f in fields)

	def __operators__(self):
		self._operators['drop'] = SQLiteDropOperator(self)
		self._operators['add'] = SQliteAddOperator(self)
		self._operators['add_fk'] = SQliteAddForeignKeyOperator(self)
		self._operators['rename_to'] = SQliteRenameOperator(self)
	
	@operator_delegating_metod
	def alter(self, field: FieldSchema):
		self.drop(field.name)
		self.add(field)
	
	def get_table_name(self) -> str:
		return self._table

	def get_state(self) -> dict:
		return self._state
	
	def get_schema(self) -> object:
		return self._schema.__class__()
	
	def to_str(self) -> str:
		separator = "\n"
		applied_operators = []
		for operator in self._operators.values():
			if operator:
				operator.mutate_disposer_state()
				applied_operators.append(operator.to_str())
		return separator.join(applied_operators)

class SQLiteSchemaEngine(SchemaEngine):
	field_schema = MySQLFieldSchema
	foreign_key_schema = MySQLForeignKeySchema
	primary_key_schema = MySQLPrimaryKeySchema

	def __operators__(self):
		self._operators['delete_table'] = SQliteDeleteTableOperation()
		self._operators['create_table'] = CreateTableOperator()
		self._operators['alter_table'] = ChangeTableOperator()

	def alter_table(self, table: str, fields: Iterable[FieldSchema]) -> SQLiteTableSchemaEngine:
		table_schema_engine = SQLiteTableSchemaEngine(self, table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine