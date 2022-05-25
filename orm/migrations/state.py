from typing import Iterable
from mymvc2.apps.app import App
from .migration import Migration
from .operations import *

def deconstruct_model(model: type) -> dict:
	return {
		'fields': dict(map(lambda f: (f.name, f.deconstruct()), model.meta['all_fields'])),
	}

class State:
	def __init__(self):
		self.state = {}

	@classmethod
	def from_app(cls, app: App) -> object:
		instance = cls()
		for model in app.get_models():
			instance.state[model.meta['name']] = deconstruct_model(model)
		return instance

	@classmethod
	def from_migrations(cls, migration_list: Iterable[Migration]) -> object:
		instance = cls()
		for migration in migration_list:
			migration.apply_to_state(instance.state)
		return instance

	def _field_compare(self, get_alter_table_operation, field: str, from_field: dict, to_field: dict):
		for param in to_field.keys():
			if from_field.get(param) != to_field.get(param):
				get_alter_table_operation().add_change_field_suboperation(field, to_field)
				break

	def _deep_compare(self, migration: Migration, table: str, from_meta: dict, to_meta: dict):
		from_fields = from_meta['fields']
		to_fields = to_meta['fields']

		old_fields_copy = from_fields.copy()
		alter_operation = None

		def get_alter_table_operation() -> AlterTableOperation:
			nonlocal alter_operation, migration
			if alter_operation is None:
				alter_operation = migration.add_change_table_operation(table, from_meta)
			return alter_operation

		for field, definition in to_fields.items():
			try:
				del old_fields_copy[field]
			except KeyError:
				get_alter_table_operation().add_create_field_suboperation(field, definition)
			else:
				self._field_compare(get_alter_table_operation, field, from_fields[field], to_fields[field])
		for field in old_fields_copy.keys():
			get_alter_table_operation().add_delete_field_suboperation(field)

	def _base_compare(self, migration: Migration, from_state: dict, to_state: dict):
		old_state_copy = from_state.copy()
		for table, meta in to_state.items():
			try:
				del old_state_copy[table]
			except KeyError:
				migration.add_create_table_operation(table, meta)
			else:
				old_meta = from_state[table]
				self._deep_compare(migration, table, old_meta, meta)
		for table in old_state_copy.keys():
			migration.add_delete_table_operation(table)

	def compare_with(self, previous_state: object) -> Migration:
		migration = Migration()
		self._base_compare(migration, previous_state.state, self.state)
		return migration
