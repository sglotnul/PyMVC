from typing import List
from mymvc2.orm.db.schema import SchemaEngine, TableSchemaEngine

class Operation:
	def __init__(self, table: str, meta: dict={}):
		self._table = table
		self._meta = meta

	@staticmethod
	def apply_to_state(state: dict, definition: dict):
		raise NotImplementedError()

	def apply(self, schema: SchemaEngine):
		raise NotImplementedError()

	def deconstruct(self) -> dict:
		base_dict = {"table": self._table}
		base_dict.update(self._meta)
		return base_dict

class CreateTableOperation(Operation):
	@staticmethod
	def apply_to_state(state: dict, definition: dict):
		table = definition.pop("table")
		state[table] = definition

	def apply(self, schema: SchemaEngine):
		if self._meta is None:
			raise Exception("unable to create an empty table")
		schema.create_table(self._table, self._meta["fields"])

class DeleteTableOperation(Operation):
	@staticmethod
	def apply_to_state(state: dict, definition: dict):
		table = definition.pop("table")
		try:
			del state[table]
		except KeyError:
			pass

	def deconstruct(self) -> dict:
		return {"table": self._table}

	def apply(self, schema: SchemaEngine):
		schema.delete_table(self._table)

FIELDS_DICT = "fields"

class SubOperation(Operation):
	def __init__(self, field: str, meta: dict={}):
		self._meta = meta
		self._field = field

	def deconstruct(self) -> dict:
		base_dict = {"field": self._field}
		base_dict.update(self._meta)
		return base_dict

class CreateFieldSubOperation(SubOperation):
	@staticmethod
	def apply_to_state(state: dict, table: str, field: str, definition: dict):
		state[table][FIELDS_DICT][field] = definition

	def apply(self, schema: TableSchemaEngine):
		schema.add(self._field, self._meta)

class DeleteFieldSubOperation(SubOperation):
	@staticmethod
	def apply_to_state(state: dict, table: str, field: str, definition: dict):
		del state[table][FIELDS_DICT][field]

	def apply(self, schema: TableSchemaEngine):
		schema.drop(self._field)

class ChangeFieldSubOperation(CreateFieldSubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.alter(self._field, self._meta)

SUBOPERATION_CLS = {
	"CREATE_FIELD": CreateFieldSubOperation,
	"DELETE_FIELD": DeleteFieldSubOperation,
	"CHANGE_FIELD": ChangeFieldSubOperation,
}

def get_suboperation_cls(operation_type: str) -> type:
	operation_cls = SUBOPERATION_CLS.get(operation_type)
	assert operation_cls, f"{operation_type} is unregistered operation"
	return operation_cls

class AlterTableOperation(Operation):
	@staticmethod
	def apply_to_state(state: dict, definition: dict):
		table = definition.pop("table")
		for suboperation_type, inner in definition.items():
			for suboperation in inner:
				field = suboperation.pop("field")
				get_suboperation_cls(suboperation_type).apply_to_state(state, table, field, suboperation)
	
	def __init__(self, table: str, meta: dict={}):
		super().__init__(table, meta)

		self._suboperations = {}

	def _get_same_suboperations_list(self, suboperation_type: str) -> List[SubOperation]:
		same_suboperations_list = self._suboperations.get(suboperation_type)
		if same_suboperations_list is None:
			same_suboperations_list = []
			self._suboperations[suboperation_type] = same_suboperations_list
		return same_suboperations_list

	def _add_suboperation(self, suboperation_type: str, suboperation: Operation):
		same_suboperation_list = self._get_same_suboperations_list(suboperation_type)
		same_suboperation_list.append(suboperation)

	def add_create_field_suboperation(self, suboperation: CreateFieldSubOperation):
		self._add_suboperation("CREATE_FIELD", suboperation)

	def add_delete_field_suboperation(self, suboperation: DeleteFieldSubOperation):
		self._add_suboperation("DELETE_FIELD", suboperation)

	def add_change_field_suboperation(self, suboperation: ChangeFieldSubOperation):
		self._add_suboperation("CHANGE_FIELD", suboperation)

	def apply(self, schema: SchemaEngine):
		schema = schema.alter_table(self._table, self._meta['fields'])
		for suboperations in self._suboperations.values():
			for suboperation in suboperations:
				suboperation.apply(schema)

	def deconstruct(self) -> dict:
		d = {"table": self._table}
		for suboperation_type, suboperations in self._suboperations.items():
			d[suboperation_type] = list(map(lambda suo: suo.deconstruct(), suboperations))
		return d

	def __bool__(self) -> bool:
		return bool(self._suboperations)