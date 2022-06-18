from re import search
from typing import Iterable, Union
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

	def __post_init__(self):
		raise Exception("foreign key data type wasn't redefined")
	
@dataclass
class PrimaryKeySchema(FieldSchema):
	def __post_init__(self):
		raise Exception("primary key data type wasn't redefined")

@dataclass
class ManyToManySchema(FieldSchema):
	references: str

	def __post_init__(self):
		raise Exception("many-to-many data type wasn't redefined")

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
	def add(self, field: Union[str, FieldSchema], *data):
		if not isinstance(field, FieldSchema):
			field = self.get_field(field, *data)
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		if isinstance(field, ManyToManySchema):
			return self.add_m2m(field)
		self._operators['add'].set(field)

	@operator_delegating_metod
	def drop(self, field: str):
		self._operators['drop'].set(field)

	@operator_delegating_metod
	def alter(self, field: Union[str, FieldSchema], *data):
		if not isinstance(field, FieldSchema):
			field = self.get_field(field, *data)
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		if isinstance(field, ManyToManySchema):
			return self.add_m2m(field)
		self._operators['alter'].set(field)

	@operator_delegating_metod
	def rename_to(self, to_name: str):
		self._operators['rename_to'].set(to_name)

	@operator_delegating_metod
	def add_foreign_key(self, field: Union[str, ForeignKeySchema], *data):
		if not isinstance(field, ForeignKeySchema):
			field = self.get_field(field, *data)
		self._operators['add_fk'].set(field)

	@operator_delegating_metod
	def add_m2m(self, field: Union[str, ManyToManySchema], *data):
		if not isinstance(field, ManyToManySchema):
			field = self.get_field(field, *data)
		bounding_table_name = self._table + "_" + field.references
		table_col, rel_table_col = self._table + "_id", field.references + "_id"
		self._schema.create_table(bounding_table_name, [(table_col, f"FK({self._table})", None, False), (rel_table_col, f"FK({field.references})", None, False)])
	
	def get_field(self, *args, **kwargs) -> FieldSchema:
		return self._schema.get_field(*args, **kwargs)

class SchemaEngine(OperatorRegistry):
	field_schema = FieldSchema
	foreign_key_schema = ForeignKeySchema
	primary_key_schema = PrimaryKeySchema
	many_to_many_schema = ManyToManySchema

	def __operators__(self):
		self._operators['delete_table'] = Operator()
		self._operators['create_table'] = Operator()
		self._operators['alter_table'] = Operator()

	@operator_delegating_metod
	def create_table(self, table: str, fields: Iterable[Union[FieldSchema, Iterable[any]]], **kwargs) -> str:
		fields = tuple(map(lambda f: f if isinstance(f, FieldSchema) else self.get_field(*f), fields))
		for f in fields:
			if isinstance(f, ManyToManySchema):
				self.alter_table(table, fields).add_m2m(f)
		self._operators['create_table'].set(table, fields, **kwargs)

	@operator_delegating_metod
	def delete_table(self, table: str) -> str:
		self._operators['delete_table'].set(table)

	def alter_table(self, table: str, fields: Iterable[Union[FieldSchema, Iterable[any]]]) -> TableSchemaEngine:
		fields = tuple(map(lambda f: f if isinstance(f, FieldSchema) else self.get_field(*f), fields))
		table_schema_engine = TableSchemaEngine(self, table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine

	def get_field(self, field: str, data_type: str, *data) -> FieldSchema:
		references = search(r'FK\((.+?)\)', data_type)
		if references:
			return self.foreign_key_schema(field, data_type, *data, references.group(1))
		references = search(r'M2M\((.+?)\)', data_type)
		if references:
			return self.many_to_many_schema(field, data_type, *data, references.group(1))
		if data_type == "PK":
			return self.primary_key_schema(field, data_type, *data)
		return self.field_schema(field, data_type, *data)