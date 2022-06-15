from typing import List
from pafmvc.orm.migrations.operations.base import Operation
from pafmvc.orm.db.schema import SchemaEngine, TableSchemaEngine

def get_field(schema: SchemaEngine, field: str, meta: dict):
	if meta.get('references', None):
		return schema.foreign_key_schema(field, meta['data_type'], meta['default'], meta['null'], meta['references'])
	if meta.get('primary_key', None):
		return schema.primary_key_schema(field, meta['data_type'], meta['default'], meta['null'])
	return schema.field_schema(field, meta['data_type'], meta['default'], meta['null'])

class CreateTableOperation(Operation):
	def __init__(self, *args, fields: dict, **kwargs):
		super().__init__(*args, **kwargs)
		self._fields = fields if fields is not None else {}

	def apply(self, schema: SchemaEngine):
		schema.create_table(self._table, map(lambda f: get_field(schema, *f), self._fields.items()))

	def apply_to_state(self, state: object):
		state.set_model(self._table, self._fields, self._meta)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['fields'] = self._fields
		data.update(self._meta)
		return data

class DeleteTableOperation(Operation):
	def apply(self, schema: SchemaEngine):
		schema.delete_table(self._table)

	def apply_to_state(self, state: object):
		state.del_model(self._table)

FIELDS_DICT = "fields"

class SubOperation(Operation):
	def __init__(self, table: str, field: str, **meta):
		super().__init__(table, **meta)
		self._field = field

	def deconstruct(self) -> dict:
		return {"field": self._field}

	def __bool__(self) -> bool:
		return bool(super().__bool__() and self._field)

class CreateFieldSubOperation(SubOperation):
	def __init__(self, *args, data_type: str=None, default: any=None, null: bool=False, **meta):
		super().__init__(*args, **meta)
		self._data_type = data_type
		assert self._data_type is not None
		self._default = default
		self._null = null

	def apply(self, schema: TableSchemaEngine):
		schema.add(get_field(schema, self._field, self._get_data()))

	def apply_to_state(self, state: object):
		state.set_field(self._field, self._data_type, self._default, self._null, self._meta)

	def _get_data(self) -> dict:
		data = {
			'data_type': self._data_type,
			'default': self._default,
			'null': self._null,
		}
		data.update(self._meta)
		return data

	def deconstruct(self) -> dict:
		data = {"field": self._field}
		data.update(self._get_data())
		return data

class DeleteFieldSubOperation(SubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.drop(self._field)

	def apply_to_state(self, state: object):
		state.del_field(self._field)

class ChangeFieldSubOperation(CreateFieldSubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.alter(get_field(schema, self._field, self._get_data()))

SUBOPERATION_CLS = {
	"CREATE_FIELD": CreateFieldSubOperation,
	"DELETE_FIELD": DeleteFieldSubOperation,
	"CHANGE_FIELD": ChangeFieldSubOperation,
}

class AlterTableOperation(Operation):	
	def __init__(self, *args, fields=None, **kwargs):
		super().__init__(*args, **kwargs)
		self._fields = fields or {}
		self._suboperations = {}

		for suboperation_type, suboperation_list in self._meta.items():
			if SUBOPERATION_CLS.get(suboperation_type) is None:
				continue
			for suboperation_definition in suboperation_list:
				field = suboperation_definition.pop("field")
				self._add_suboperation(suboperation_type, field, **suboperation_definition)

	def _get_same_suboperations_list(self, suboperation_type: str) -> List[SubOperation]:
		same_suboperations_list = self._suboperations.get(suboperation_type)
		if same_suboperations_list is None:
			same_suboperations_list = []
			self._suboperations[suboperation_type] = same_suboperations_list
		return same_suboperations_list

	def _add_suboperation(self, suboperation_type: str, field: str, **kwargs):
		suboperation_cls = SUBOPERATION_CLS[suboperation_type]
		same_suboperation_list = self._get_same_suboperations_list(suboperation_type)
		same_suboperation_list.append(suboperation_cls(self._table, field, **kwargs))

	def add_create_field_suboperation(self, field: str, data: dict):
		self._add_suboperation("CREATE_FIELD", field, **data)

	def add_delete_field_suboperation(self, field: str):
		self._add_suboperation("DELETE_FIELD", field)

	def add_change_field_suboperation(self, field: str, data: dict):
		self._add_suboperation("CHANGE_FIELD", field, **data)

	def apply(self, schema: SchemaEngine):
		schema = schema.alter_table(self._table, map(lambda f: get_field(schema, *f), self._fields.items()))
		for suboperations in self._suboperations.values():
			for suboperation in suboperations:
				suboperation.apply(schema)

	def apply_to_state(self, state: object):
		for suboperation_list in self._suboperations.values():
			for suboperation in suboperation_list:
				suboperation.apply_to_state(state.models[self._table])

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		for suboperation_type, suboperations in self._suboperations.items():
			suboperation_list = list(map(lambda suo: suo.deconstruct(), suboperations))
			if suboperation_list:
				data[suboperation_type] = suboperation_list
		return data

	def __bool__(self) -> bool:
		return bool(self._suboperations)