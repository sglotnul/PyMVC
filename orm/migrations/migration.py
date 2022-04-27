import json
from typing import List
from mymvc2.orm.migrations.operations.base import Operation, CreateTableOperation, DeleteTableOperation, AlterTableOperation

#Преставляет собой одну миграцию. Содержит информацию обо все примененных в ней операциях
OPERATION_CLS = {
	"CREATE_TABLE": CreateTableOperation,
	"DELETE_TABLE": DeleteTableOperation,
	"CHANGE_TABLE": AlterTableOperation,
}

class Migration:
	@staticmethod
	def apply_to_state(state: dict, migration_inner: dict):
		for operation_type, inner in migration_inner.items():
			for operation in inner:
				OPERATION_CLS[operation_type].apply_to_state(state, operation)
				
	def __init__(self):
		self._operations = {}

	def _get_same_operations_list(self, operation_type: str) -> List[Operation]:
		same_operations_list = self._operations.get(operation_type)
		if same_operations_list is None:
			same_operations_list = []
			self._operations[operation_type] = same_operations_list
		return same_operations_list

	def _add_operation(self, operation_type: str, operation: Operation):
		same_operations_list = self._get_same_operations_list(operation_type)
		same_operations_list.append(operation)

	def _execute(self, executor, query: str):
		executor(query, script=True)

	def add_create_table_operation(self, operation: CreateTableOperation):
		self._add_operation("CREATE_TABLE", operation)

	def add_delete_table_operation(self, operation: DeleteTableOperation):
		self._add_operation("DELETE_TABLE", operation)

	def add_change_table_operation(self, operation: AlterTableOperation):
		self._add_operation("CHANGE_TABLE", operation)

	def to_json(self) -> str:
		deconstructed_migration = {}
		for operation_type, operations in self._operations.items():
			deconstructed_migration[operation_type] = list(map(lambda o: o.deconstruct(), operations))
		return json.dumps(deconstructed_migration)

	def apply(self, executor: object):
		schema = executor.schema_engine()
		for operation_list in self._operations.values():
			for operation in operation_list:
				operation.apply(schema)
		self._execute(executor, str(schema))

	def __bool__(self) -> bool:
		return bool(self._operations)