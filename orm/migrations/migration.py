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
	def __init__(self, entry: dict={}):
		self._operations = {}

		for operation_type, operations_list in entry.items():
			assert OPERATION_CLS.get(operation_type, None), f"{operation_type} is invalid operation type"
			for operation_definition in operations_list:
				table = operation_definition.pop('table')
				self._add_operation(operation_type, table, **operation_definition)
	
	def _get_same_operations_list(self, operation_type: str) -> List[Operation]:
		same_operations_list = self._operations.get(operation_type)
		if same_operations_list is None:
			same_operations_list = []
			self._operations[operation_type] = same_operations_list
		return same_operations_list

	def _add_operation(self, operation_type: str, table: str, **kwargs) -> Operation:
		operation_cls = OPERATION_CLS[operation_type]
		same_operations_list = self._get_same_operations_list(operation_type)
		operation = operation_cls(table, **kwargs)
		same_operations_list.append(operation)
		return operation

	def _execute(self, executor, query: str):
		executor(query, script=True)

	def add_create_table_operation(self, table: str, data: dict) -> Operation:
		return self._add_operation("CREATE_TABLE", table, **data)

	def add_delete_table_operation(self, table: str) -> Operation:
		return self._add_operation("DELETE_TABLE", table)

	def add_change_table_operation(self, table: str, data: dict) -> Operation:
		return self._add_operation("CHANGE_TABLE", table, **data)

	def deconstruct(self) -> dict:
		deconstructed_migration = {}
		for operation_type, operations in self._operations.items():
			operations_list = list(map(lambda o: o.deconstruct(), operations))
			if operations_list:
				deconstructed_migration[operation_type] = operations_list
		return deconstructed_migration

	def apply(self, executor: object):
		schema = executor.schema_engine()
		for operation_list in self._operations.values():
			for operation in operation_list:
				operation.apply(schema)
		self._execute(executor, schema.to_str())

	def apply_to_state(self, state: object):
		for operation_list in self._operations.values():
			for operation in operation_list:
				operation.apply_to_state(state)

	def __bool__(self) -> bool:
		return bool(self._operations)