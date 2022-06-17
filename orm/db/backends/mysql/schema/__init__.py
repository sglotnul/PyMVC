from typing import Iterable
from dataclasses import dataclass
from pafmvc.orm.db.schema import FieldSchema, ForeignKeySchema, PrimaryKeySchema, SchemaEngine, TableSchemaEngine
from .operators import *

@dataclass
class MySQLFieldSchema(FieldSchema):
	def to_sql(self) -> str:
		FIELD_TMP = "{} {}"
		NULL_POSTFIX = "NULL"
		NOT_NULL_POSTFIX = "NOT NULL"
		DEFAULT_POSTFIX = "DEFAULT \"{}\""
		separator = " "

		raw_field_sql = FIELD_TMP.format(self.name, self.data_type)
		if self.default is not None:
			return raw_field_sql + separator + DEFAULT_POSTFIX.format(self.default)
		postfix = NOT_NULL_POSTFIX if not self.null else NULL_POSTFIX
		return raw_field_sql + separator + postfix

@dataclass
class MySQLForeignKeySchema(ForeignKeySchema, MySQLFieldSchema):
	def __post_init__(self):
		self.data_type = "INT"

@dataclass
class MySQLPrimaryKeySchema(PrimaryKeySchema, MySQLFieldSchema):
	def __post_init__(self):
		self.data_type = "INT"

class MySQLTableSchemaEngine(TableSchemaEngine):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._init_operator = AlterTable()
		self._init_operator.set(self._table)

	def __operators__(self):
		self._operators['drop'] = DropOperator()
		self._operators['add'] = AddOperator()
		self._operators['alter'] = AlterOperator()
		self._operators['add_fk'] = AddForeignKeyOperator()
		self._operators['rename_to'] = RenameOperator()

	def to_str(self) -> str:
		separator = ",\n"
		return self._init_operator.to_str() + "\n" + separator.join(operator.to_str() for operator in self._operators.values() if operator) + ";"

class MySQLSchemaEngine(SchemaEngine):
	field_schema = MySQLFieldSchema
	foreign_key_schema = MySQLForeignKeySchema
	primary_key_schema = MySQLPrimaryKeySchema
		
	def alter_table(self, table: str, fields: Iterable[FieldSchema]) -> MySQLTableSchemaEngine:
		table_schema_engine = MySQLTableSchemaEngine(self, table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine

	def __operators__(self):
		self._operators['delete_table'] = DeleteTableOperator()
		self._operators['create_table'] = CreateTableOperator()
		self._operators['alter_table'] = ChangeTableOperator()