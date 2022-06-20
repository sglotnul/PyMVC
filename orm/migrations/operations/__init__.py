from typing import List
from pafmvc.orm.migrations.operations.base import Operation
from pafmvc.orm.db.schema import SchemaEngine, TableSchemaEngine
from ..state import FieldState, ModelState

class BaseOperation(Operation):
	def __init__(self, table: str, fields: dict=None, **meta):
		super().__init__(table, **meta)
		self._fields = fields or {}

class CreateTableOperation(BaseOperation):
	@classmethod
	def from_entry(cls, entry: dict) -> object:
		fields = dict(map(lambda e: (e[0], FieldState(*e[1])), entry.pop("fields").items()))
		return cls(entry.pop('table'), fields, **entry)

	def apply(self, schema: SchemaEngine):
		fields = tuple(map(lambda e: schema.get_field(e[0], *e[1].deconstruct()), self._fields.items()))
		schema.create_table(self._table, fields)

	def apply_to_state(self, state: object):
		model = ModelState()
		for entry in self._fields.items():
			model.set_field(*entry)
		state.set_model(self._table, model)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['fields'] = dict(map(lambda e: (e[0], e[1].deconstruct()), self._fields.items()))
		return data

class DeleteTableOperation(BaseOperation):
	def apply(self, schema: SchemaEngine):
		fields =  tuple(map(lambda e: schema.get_field(e[0], *e[1].deconstruct()), self._fields.items()))
		schema.delete_table(self._table, fields)

	def apply_to_state(self, state: object):
		state.del_model(self._table)

FIELDS_DICT = "fields"

class SubOperation(Operation):
	def __init__(self, field: str, data: FieldState=None, **kwargs):
		self._field = field
		self._data = data
		self._meta = kwargs

	@classmethod
	def from_entry(cls, entry: dict) -> object:
		return cls(entry.pop("field"), **entry)

	def deconstruct(self) -> dict:
		data = {'field': self._field}
		data.update(self._meta)
		return data

	def __bool__(self) -> bool:
		return bool(super().__bool__() and self._field)

class CreateFieldSubOperation(SubOperation):
	@classmethod
	def from_entry(cls, entry: dict) -> object:
		return cls(entry.pop("field"), FieldState(*entry.pop("data")), **entry)

	def apply(self, schema: TableSchemaEngine):
		field = schema.get_field(self._field, *self._data.deconstruct())
		schema.add(field)

	def apply_to_state(self, state: object):
		state.set_field(self._field, self._data)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['data'] = self._data.deconstruct()
		return data

class DeleteFieldSubOperation(SubOperation):
	def apply(self, schema: TableSchemaEngine):
		field = schema.get_field(self._field, *self._data.deconstruct())
		schema.drop(field)

	def apply_to_state(self, state: object):
		state.del_field(self._field)

class ChangeFieldSubOperation(CreateFieldSubOperation):
	def apply(self, schema: TableSchemaEngine):
		field = schema.get_field(self._field, *self._data.deconstruct())
		schema.alter(field)

SUBOPERATION_CLS = {
	"CREATE_FIELD": CreateFieldSubOperation,
	"DELETE_FIELD": DeleteFieldSubOperation,
	"CHANGE_FIELD": ChangeFieldSubOperation,
}

class AlterTableOperation(BaseOperation):	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._suboperations = {}	

	@classmethod
	def from_entry(cls, entry: dict) -> object:
		instance = cls(entry.pop('table'), **entry)
		for suboperation_type, suboperation_list in entry.items():
			suboperation_cls = SUBOPERATION_CLS.get(suboperation_type, None)
			if suboperation_cls is not None:
				for suboperation_definition in suboperation_list:
					instance._add_suboperation(suboperation_type, suboperation_cls.from_entry(suboperation_definition))
		return instance

	def _get_same_suboperations_list(self, suboperation_type: str) -> List[SubOperation]:
		same_suboperations_list = self._suboperations.get(suboperation_type)
		if same_suboperations_list is None:
			same_suboperations_list = []
			self._suboperations[suboperation_type] = same_suboperations_list
		return same_suboperations_list

	def _add_suboperation(self, suboperation_type: str, suboperation: SubOperation) -> SubOperation:
		same_suboperation_list = self._get_same_suboperations_list(suboperation_type)
		same_suboperation_list.append(suboperation)
		return suboperation

	def add_create_field_suboperation(self, field: str, data: FieldState, **kwargs) -> SubOperation:
		cls = SUBOPERATION_CLS["CREATE_FIELD"]
		return self._add_suboperation("CREATE_FIELD", cls(field, data, **kwargs))

	def add_delete_field_suboperation(self, field: str, data: FieldState, **kwargs) -> SubOperation:
		cls = SUBOPERATION_CLS["DELETE_FIELD"]
		return self._add_suboperation("DELETE_FIELD", cls(field, data, **kwargs))

	def add_change_field_suboperation(self, field: str, data: FieldState, **kwargs) -> SubOperation:
		cls = SUBOPERATION_CLS["CHANGE_FIELD"]
		return self._add_suboperation("CHANGE_FIELD", cls(field, data, **kwargs))

	def apply(self, schema: SchemaEngine):
		fields =  tuple(map(lambda e: schema.get_field(e[0], *e[1].deconstruct()), self._fields.items()))
		schema = schema.alter_table(self._table, fields)
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