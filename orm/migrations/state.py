from typing import Tuple
from mymvc2.apps.app import App
from mymvc2.orm.migrations.migration import Migration
from mymvc2.orm.migrations.operations.base import CreateTableOperation, DeleteTableOperation, AlterTableOperation, CreateFieldSubOperation, DeleteFieldSubOperation, ChangeFieldSubOperation


class StateComparer:
	def __init__(self, disposer: object): 
		self.state = disposer.state
		self.app = disposer.app

	def _field_compare(self, alter_operation: AlterTableOperation, field: str, from_field: dict, to_field: dict):
		for param in to_field.keys():
			if from_field.get(param) != to_field.get(param):
				alter_operation.add_change_field_suboperation(ChangeFieldSubOperation(field, to_field))
				break

	def _deep_compare(self, migration: Migration, table: str, from_meta: dict, to_meta: dict):
		from_fields = from_meta['fields']
		to_fields = to_meta['fields']

		old_fields_copy = from_fields.copy()
		alter_operation = AlterTableOperation(table, from_meta)

		for field, definition in to_fields.items():
			try:
				del old_fields_copy[field]
			except KeyError:
				alter_operation.add_create_field_suboperation(CreateFieldSubOperation(field, definition))
			else:
				self._field_compare(alter_operation, field, from_fields[field], to_fields[field])
		for field in old_fields_copy.keys():
			alter_operation.add_delete_field_suboperation(DeleteFieldSubOperation(field))

		if alter_operation:
			migration.add_change_table_operation(alter_operation)

	def _base_compare(self, migration: Migration, from_state: dict, to_state: dict):
		old_state_copy = from_state.copy()
		for table, meta in to_state.items():
			try:
				del old_state_copy[table]
			except KeyError:
				migration.add_create_table_operation(CreateTableOperation(table, meta))
			else:
				old_meta = from_state[table]
				self._deep_compare(migration, table, old_meta, meta)
		for table in old_state_copy.keys():
			migration.add_delete_table_operation(DeleteTableOperation(table))

	def compare(self, previous_state: object) -> Migration:
		migration = Migration()
		self._base_compare(migration, previous_state.state, self.state)
		return migration

class State:
	def __init__(self, app: App):
		self.app = app
		self.state = {}
		self.comparer = StateComparer(self)

	def build(self):
		for model in self.app.get_models():
			meta = model.__meta__
			self.state[meta['name']] = {
				'fields': dict(map(lambda f: (f.name, f.deconstruct()), meta['all_fields'])),
			}

	def mutate(self, migration_inner: dict):
		Migration.apply_to_state(self.state, migration_inner)
