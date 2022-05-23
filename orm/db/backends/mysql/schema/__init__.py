from mymvc2.orm.db.schema import SchemaEngine, TableSchemaEngine
from .operators import *

class MySQLTableSchemaEngine(TableSchemaEngine):
	def reset(self):
		self._operators['alter_table'] = AlterTable()
		self._operators['alter_table'].set(self._table)
		self._operators['drop'] = DropOperator()
		self._operators['add'] = AddOperator()
		self._operators['alter'] = AlterOperator()
		self._operators['add_fk'] = AddForeignKeyOperator()
		self._operators['rename_to'] = RenameOperator()

	def to_str(self) -> str:
		separator = ",\n"
		return separator.join(operator.to_str() for operator in self._operators.values() if operator) + ";"

class MySQLSchemaEngine(SchemaEngine):
	def alter_table(self, table: str, fields: dict) -> MySQLTableSchemaEngine:
		table_schema_engine = MySQLTableSchemaEngine(table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine

	def reset(self):
		self._operators['delete_table'] = DeleteTableOperator()
		self._operators['create_table'] = CreateTableOperator()
		self._operators['alter_table'] = ChangeTableOperator()

