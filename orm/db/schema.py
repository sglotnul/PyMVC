from re import search
from typing import Tuple
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

class TableSchemaEngine(OperatorRegistry):
	def __init__(self, schema: OperatorRegistry, table: str, fields: Tuple[FieldSchema]):
		self._schema = schema
		self._table = table
		self._fields = tuple(fields)
		super().__init__()

	def __operators__(self):
		self._operators['drop'] = Operator()
		self._operators['add'] = Operator()
		self._operators['alter'] = Operator()
		self._operators['add_fk'] = Operator()
		self._operators['rename_to'] = Operator()

	@operator_delegating_metod
	def add(self, field: FieldSchema):
		if isinstance(field, ManyToManySchema):
			return self.add_m2m(field)
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		self._operators['add'].set(field)

	@operator_delegating_metod
	def drop(self, field: FieldSchema):
		if isinstance(field, ManyToManySchema):
			return self.drop_m2m(field)
		self._operators['drop'].set(field.name)

	@operator_delegating_metod
	def alter(self, field: FieldSchema):
		if isinstance(field, ManyToManySchema):
			return self.add_m2m(field)
		if isinstance(field, ForeignKeySchema):
			self.add_foreign_key(field)
		for f in self._fields:
			if f.name == field.name and isinstance(f, ManyToManySchema):
				return self.drop_m2m(f)
		self._operators['alter'].set(field)

	@operator_delegating_metod
	def rename_to(self, to_name: str):
		self._operators['rename_to'].set(to_name)

	@operator_delegating_metod
	def add_foreign_key(self, field: ForeignKeySchema):
		self._operators['add_fk'].set(field)

	def _get_m2m_table_data(self, field: ManyToManySchema) -> Tuple[any]:
		bounding_table_name = self._table + "_" + field.references
		fields = (
			self.get_field(self._table + "_id", f"FK({self._table})", None, False),
			self.get_field(field.references + "_id", f"FK({field.references})", None, False),
		)
		return (bounding_table_name, fields)

	@operator_delegating_metod
	def add_m2m(self, field: ManyToManySchema):
		self._schema.create_table(*self._get_m2m_table_data(field))

	@operator_delegating_metod
	def drop_m2m(self, field: ManyToManySchema):
		self._schema.delete_table(self._table + "_" + field.references)
	
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
	def create_table(self, table: str, fields: Tuple[FieldSchema], **kwargs) -> str:
		field_list = []
		alter_schema = None
		for field in fields:	
			if isinstance(field, ManyToManySchema):
				alter_schema = alter_schema or self.alter_table(table, fields)
				alter_schema.add_m2m(field)
			else:
				field_list.append(field)
		self._operators['create_table'].set(table, field_list, **kwargs)

	@operator_delegating_metod
	def delete_table(self, table: str, fields: Tuple[FieldSchema]=()) -> str:
		for field in fields:
			alter_schema = None
			if isinstance(field, ManyToManySchema):
				alter_schema = alter_schema or self.alter_table(table, fields)
				alter_schema.drop_m2m(field)
		self._operators['delete_table'].set(table)

	def alter_table(self, table: str, fields: Tuple[FieldSchema]) -> TableSchemaEngine:
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