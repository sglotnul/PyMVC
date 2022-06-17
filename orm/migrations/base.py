import os, yaml
from typing import Iterable, List
from .state import State
from .migration import Migration
from pafmvc.apps.app import App
from pafmvc.orm.db.executor import BaseExecutor
from .operations import *

MIGRATION_FOLDER_NAME = "migrations"

class MigrationFileManager:
	def __init__(self, app: App):
		path = os.path.join(app.get_app_path(), MIGRATION_FOLDER_NAME)
		if not os.path.isdir(path):
			os.mkdir(path)
		self._folder = path

	def _get_sorted_file_list(self) -> Iterable[str]:
		return sorted(os.listdir(self._folder), key=lambda f: int(f.rpartition(".")[0]))

	def _get_previous_migration_files(self) -> Iterable[str]:
		return map(lambda filename: os.path.join(self._folder, filename), self._get_sorted_file_list())

	def _get_previous_migrations(self) -> List[Migration]:
		migrations = []
		for file in self._get_previous_migration_files():
			with open(file) as f:
				file_inner = f.read()
				if file_inner:
					migrations.append(Migration.from_entry(yaml.load(file_inner, Loader=yaml.Loader)))
		return migrations

	def commit(self, migration: Migration):
		if migration:
			postfix = ".yaml"
			index_pointer = 1
			try:
				index_pointer = int(self._get_sorted_file_list()[-1].rpartition(".")[0]) + 1
			except IndexError:
				pass
			migration_path = os.path.join(self._folder, str(index_pointer) + postfix)
			with open(migration_path, 'w+') as migration_file:
				migration_file.write(yaml.dump(migration.deconstruct(), Dumper=yaml.Dumper))

class MigrationEngine:
	def __init__(self, app: App):
		self._app = app
		self.file_manager = MigrationFileManager(app)

	def _build_state(self) -> State:
		return State(app=self._app)

	def _migrate_state(self) -> State:
		return State(migrations=self.file_manager._get_previous_migrations())

	def _field_compare(self, get_operation, field: str, from_field: dict, to_field: dict):
		if from_field != to_field:
			get_operation().add_change_field_suboperation(field, to_field.deconstruct())

	def _deep_compare(self, migration: Migration, table: str, from_meta: dict, to_meta: dict) -> Migration:
		from_fields = from_meta.fields
		to_fields = to_meta.fields

		old_fields_copy = from_fields.copy()
		alter_operation = None

		def get_alter_table_operation() -> AlterTableOperation:
			nonlocal alter_operation, migration
			if alter_operation is None:
				alter_operation = migration.add_change_table_operation(table, from_meta.deconstruct())
			return alter_operation

		for field, field_meta in to_fields.items():
			try:
				del old_fields_copy[field]
			except KeyError:
				get_alter_table_operation().add_create_field_suboperation(field, field_meta.deconstruct())
			else:
				self._field_compare(get_alter_table_operation, field, from_fields[field], to_fields[field])
		for field in old_fields_copy.keys():
			get_alter_table_operation().add_delete_field_suboperation(field)
		return migration

	def _base_compare(self, migration: Migration, from_state: dict, to_state: dict) -> Migration:
		old_state_copy = from_state.copy()
		for table, meta in to_state.items():
			try:
				del old_state_copy[table]
			except KeyError:
				migration.add_create_table_operation(table, meta.deconstruct())
			else:
				old_meta = from_state[table]
				self._deep_compare(migration, table, old_meta, meta)
		for table in old_state_copy.keys():
			migration.add_delete_table_operation(table)
		return migration

	def get_changes(self) -> Migration:
		prev_state = self._migrate_state()
		state = self._build_state()

		return self._base_compare(Migration(), prev_state.models, state.models)
		
	def migrate(self, executor: BaseExecutor):
		new_migraton = self.get_changes()
		new_migraton.apply(executor)

		self.file_manager.commit(new_migraton)
