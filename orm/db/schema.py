from typing import Iterable
from dataclasses import dataclass
from pafmvc.orm.db.operator import OperatorRegistry, Operator, operator_delegating_metod

@dataclass	
class FieldSchema:
	name: str
	data_type: str
	default: any
	null: bool

	def to_sql(self) -> str:
		raise NotImplementedError()

@dataclass
class ForeignKeySchema(FieldSchema):
	references: str
	
@dataclass
class PrimaryKeySchema(FieldSchema):
	pass

class TableSchemaEngine(OperatorRegistry):
	def __init__(self, schema: OperatorRegistry, table: str, fields: Iterable[FieldSchema]):
		self._schema = schema
		self._table = table
		self._fields = fields
		super().__init__()

	def __operators__(self):
		self._operators['drop'] = Operator()
		self._operators['add'] = Operator()
		self._operators['alter'] = Operator()
		self._operators['add_fk'] = Operator()
		self._operators['rename_to'] = Operator()

	@operator_delegating_metod
	def add(self, field: FieldSchema):
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		self._operators['add'].set(field)

	@operator_delegating_metod
	def drop(self, field: str):
		self._operators['drop'].set(field)

	@operator_delegating_metod
	def alter(self, field: FieldSchema):
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		self._operators['alter'].set(field)

	@operator_delegating_metod
	def rename_to(self, to_name: str):
		self._operators['rename_to'].set(to_name)

	@operator_delegating_metod
	def add_foreign_key(self, field: FieldSchema):
		self._operators['add_fk'].set(field)
	
	def get_field(self, *args, **kwargs) -> FieldSchema:
		return self._schema.get_field(*args, **kwargs)

class SchemaEngine(OperatorRegistry):
	field_schema = FieldSchema
	foreign_key_schema = ForeignKeySchema
	primary_key_schema = PrimaryKeySchema

	def __operators__(self):
		self._operators['delete_table'] = Operator()
		self._operators['create_table'] = Operator()
		self._operators['alter_table'] = Operator()

	@operator_delegating_metod
	def create_table(self, table: str, fields: Iterable[FieldSchema]) -> str:
		self._operators['create_table'].set(table, fields)

	@operator_delegating_metod
	def delete_table(self, table: str) -> str:
		self._operators['delete_table'].set(table)

	def alter_table(self, table: str, fields: Iterable[FieldSchema]) -> TableSchemaEngine:
		table_schema_engine = TableSchemaEngine(self, table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine

	def get_field(self, field: str, meta: dict) -> FieldSchema:
		if meta.get('references', None):
			return self.foreign_key_schema(field, meta['data_type'], meta['default'], meta['null'], meta['references'])
		if meta.get('primary_key', None):
			return self.primary_key_schema(field, meta['data_type'], meta['default'], meta['null'])
		return self.field_schema(field, meta['data_type'], meta['default'], meta['null'])


