from typing import List
from mymvc2.orm.migrations.operations.base import Operation, SubOperation
from mymvc2.orm.db.schema import SchemaEngine, TableSchemaEngine

class CreateTableOperation(Operation):
	def apply(self, schema: SchemaEngine):
		if self._meta is None:
			raise Exception("unable to create an empty table")
		schema.create_table(self._table, self._meta["fields"])

	def apply_to_state(self, state_dict: dict):
		state_dict[self._table] = self._meta

class DeleteTableOperation(Operation):
	def deconstruct(self) -> dict:
		return {"table": self._table}

	def apply(self, schema: SchemaEngine):
		schema.delete_table(self._table)

	def apply_to_state(self, state_dict: dict):
		try:
			del state_dict[self._table]
		except KeyError:
			pass

	def __bool__(self) -> bool:
		return bool(self._table)

FIELDS_DICT = "fields"

class CreateFieldSubOperation(SubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.add(self._field, self._meta)

	def apply_to_state(self, state_dict: dict):
		state_dict[self._table][FIELDS_DICT][self._field] = self._meta

class DeleteFieldSubOperation(SubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.drop(self._field)

	def apply_to_state(self, state_dict: dict):
		try:
			del state_dict[self._table][FIELDS_DICT][self._field]
		except KeyError:
			pass

class ChangeFieldSubOperation(CreateFieldSubOperation):
	def apply(self, schema: TableSchemaEngine):
		schema.alter(self._field, self._meta)

SUBOPERATION_CLS = {
	"CREATE_FIELD": CreateFieldSubOperation,
	"DELETE_FIELD": DeleteFieldSubOperation,
	"CHANGE_FIELD": ChangeFieldSubOperation,
}

class AlterTableOperation(Operation):	
	def __init__(self, table: str, meta: dict={}):
		self._suboperations = {}

		for suboperation_type, inner in meta.pop('suboperations', {}).items():
			suboperation_cls = SUBOPERATION_CLS.get(suboperation_type, None)
			assert suboperation_cls, "invalid suboperation type"

			for suboperation_definition in inner:
				field = suboperation_definition.pop("field")
				self._add_suboperation(suboperation_type, suboperation_cls(table, field, suboperation_definition))
				
		super().__init__(table, meta)

	def _get_same_suboperations_list(self, suboperation_type: str) -> List[SubOperation]:
		same_suboperations_list = self._suboperations.get(suboperation_type)
		if same_suboperations_list is None:
			same_suboperations_list = []
			self._suboperations[suboperation_type] = same_suboperations_list
		return same_suboperations_list

	def _add_suboperation(self, suboperation_type: str, suboperation: Operation):
		same_suboperation_list = self._get_same_suboperations_list(suboperation_type)
		same_suboperation_list.append(suboperation)

	def add_create_field_suboperation(self, field: str, meta: dict):
		suboperation_cls = SUBOPERATION_CLS['CREATE_FIELD']
		self._add_suboperation("CREATE_FIELD", suboperation_cls(self._table, field, meta))

	def add_delete_field_suboperation(self, field: str):
		suboperation_cls = SUBOPERATION_CLS['DELETE_FIELD']
		self._add_suboperation("DELETE_FIELD", suboperation_cls(self._table, field))

	def add_change_field_suboperation(self, field: str, meta: dict):
		suboperation_cls = SUBOPERATION_CLS['CHANGE_FIELD']
		self._add_suboperation("CHANGE_FIELD", suboperation_cls(self._table, field, meta))

	def apply(self, schema: SchemaEngine):
		schema = schema.alter_table(self._table, self._meta['fields'])
		for suboperations in self._suboperations.values():
			for suboperation in suboperations:
				suboperation.apply(schema)

	def apply_to_state(self, state_dict: dict):
		for suboperation_list in self._suboperations.values():
			for suboperation in suboperation_list:
				suboperation.apply_to_state(state_dict)

	def deconstruct(self) -> dict:
		data = super().deconstruct()
		data['suboperations'] = {}
		for suboperation_type, suboperations in self._suboperations.items():
			data['suboperations'][suboperation_type] = list(map(lambda suo: suo.deconstruct(), suboperations))
		return data

	def __bool__(self) -> bool:
		return bool(self._suboperations)