import json
from typing import List
from mymvc2.orm.migrations.operations.base import Operation
from mymvc2.orm.migrations import operations

#Преставляет собой одну миграцию. Содержит информацию обо все примененных в ней операциях
OPERATION_CLS = {
	"CREATE_TABLE": operations.CreateTableOperation,
	"DELETE_TABLE": operations.DeleteTableOperation,
	"CHANGE_TABLE": operations.AlterTableOperation,
}

class Migration:
	def __init__(self):
		self._operations = {}
		
	@classmethod
	def from_entry(cls, entry: dict) -> object:
		migration = cls()
		for operation_type, inner in entry.items():
			operation_cls = OPERATION_CLS.get(operation_type, None)
			assert operation_cls, "invalid operation type"
			for operation_definition in inner:
				migration._add_operation(operation_type, operation_cls.from_entry(operation_definition))
		return migration
	
	def _get_same_operations_list(self, operation_type: str) -> List[Operation]:
		same_operations_list = self._operations.get(operation_type)
		if same_operations_list is None:
			same_operations_list = []
			self._operations[operation_type] = same_operations_list
		return same_operations_list

	def _add_operation(self, operation_type: str, operation: Operation) -> Operation:
		same_operations_list = self._get_same_operations_list(operation_type)
		same_operations_list.append(operation)
		return operation

	def _execute(self, executor, query: str):
		executor(query, script=True)

	def add_create_table_operation(self, table: str, meta: dict) -> Operation:
		operation_cls = OPERATION_CLS['CREATE_TABLE']
		return self._add_operation("CREATE_TABLE", operation_cls(table, meta))

	def add_delete_table_operation(self, table: str) -> Operation:
		operation_cls = OPERATION_CLS['DELETE_TABLE']
		return self._add_operation("DELETE_TABLE", operation_cls(table))

	def add_change_table_operation(self, table: str, meta: dict) -> Operation:
		operation_cls = OPERATION_CLS['CHANGE_TABLE']
		return self._add_operation("CHANGE_TABLE", operation_cls(table, meta))

	def deconstruct(self) -> dict:
		deconstructed_migration = {}
		for operation_type, operations in self._operations.items():
			confirmed_operations = list(map(lambda o: o.deconstruct(), filter(lambda o: o, operations)))
			if confirmed_operations:
				deconstructed_migration[operation_type] = confirmed_operations
		return deconstructed_migration

	def apply(self, executor: object):
		schema = executor.schema_engine()
		for operation_list in self._operations.values():
			for operation in operation_list:
				if operation:
					operation.apply(schema)
		self._execute(executor, schema.to_str())

	def apply_to_state(self, state_dict: dict):
		for operation_list in self._operations.values():
			for operation in operation_list:
				if operation:
					operation.apply_to_state(state_dict)

	def __bool__(self) -> bool:
		return bool(self._operations)