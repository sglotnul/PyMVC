from typing import Iterable, Tuple, List
from pafmvc.orm.migrations.operations.base import Operation
from pafmvc.orm.db.schema import SchemaEngine, TableSchemaEngine

class CreateTableOperation(Operation):
	def __init__(self, *args, fields: Iterable[Iterable[any]]=(), **kwargs):
		super().__init__(*args, **kwargs)
		self._fields = fields

	def apply(self, schema: SchemaEngine):
		schema.create_table(self._table, self._fields)

	def apply_to_state(self, state: object):
		model = state.set_model(self._table)
		for field in self._fields:
			model.set_field(*field)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['fields'] = list(map(lambda f: list(f), self._fields))
		return data

class DeleteTableOperation(Operation):
	def apply(self, schema: SchemaEngine):
		schema.delete_table(self._table)

	def apply_to_state(self, state: object):
		state.del_model(self._table)

FIELDS_DICT = "fields"

class SubOperation(Operation):
	def __init__(self, table: str, field: str, **kwargs):
		super().__init__(table, **kwargs)
		self._field = field

	def deconstruct(self) -> dict:
		data = {'field': [self._field,]}
		data.update(self._meta)
		return data

	def __bool__(self) -> bool:
		return bool(super().__bool__() and self._field)

class CreateFieldSubOperation(SubOperation):
	def __init__(self, table: str, field: str, *data, **kwargs):
		super().__init__(table, field, **kwargs)
		self._data = data

	def apply(self, schema: TableSchemaEngine):
		schema.add(self._field, *self._data)

	def apply_to_state(self, state: object):
		state.set_field(self._field, *self._data)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['field'] = [self._field, *list(self._data)]
		return data

class DeleteFieldSubOperation(SubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.drop(self._field)

	def apply_to_state(self, state: object):
		state.del_field(self._field)

class ChangeFieldSubOperation(CreateFieldSubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.alter(self._field, *self._data)

SUBOPERATION_CLS = {
	"CREATE_FIELD": CreateFieldSubOperation,
	"DELETE_FIELD": DeleteFieldSubOperation,
	"CHANGE_FIELD": ChangeFieldSubOperation,
}

class AlterTableOperation(Operation):	
	def __init__(self, *args, fields: Iterable[Iterable[any]]=(), **kwargs):
		super().__init__(*args, **kwargs)
		self._fields = fields
		self._suboperations = {}	

	@classmethod
	def from_entry(cls, entry: dict) -> object:
		table = entry.pop("table")
		instance = cls(table, **entry)
		for suboperation_type, suboperation_list in entry.items():
			suboperation_cls = SUBOPERATION_CLS.get(suboperation_type, None)
			if suboperation_cls is not None:
				for suboperation_definition in suboperation_list:
					instance._add_suboperation(suboperation_type, suboperation_cls(table, *suboperation_definition.pop("field"), **suboperation_definition))
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

	def add_create_field_suboperation(self, field: str, data: Tuple[any]) -> SubOperation:
		cls = SUBOPERATION_CLS["CREATE_FIELD"]
		return self._add_suboperation("CREATE_FIELD", cls(self._table, field, *data))

	def add_delete_field_suboperation(self, field: str) -> SubOperation:
		cls = SUBOPERATION_CLS["DELETE_FIELD"]
		return self._add_suboperation("DELETE_FIELD", cls(self._table, field))

	def add_change_field_suboperation(self, field: str, data: Tuple[any]) -> SubOperation:
		cls = SUBOPERATION_CLS["CHANGE_FIELD"]
		return self._add_suboperation("CHANGE_FIELD", cls(self._table, field, *data))

	def apply(self, schema: SchemaEngine):
		schema = schema.alter_table(self._table, self._fields)
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