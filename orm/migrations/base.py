import os, json
from typing import List
from mymvc2.apps.app import App
from mymvc2.orm.migrations.state import State
from mymvc2.orm.migrations.migration import Migration
from mymvc2.orm.db.executor import BaseExecutor

MIGRATION_FOLDER_NAME = "migrations"

class MigrationFileManager:
	def __init__(self, app: App):
		path = os.path.join(app.get_app_path(), MIGRATION_FOLDER_NAME)
		if not os.path.isdir(path):
			os.mkdir(path)
		self.folder = path
		self.sorted_file_list = sorted(os.listdir(path), key=lambda file: int(file.rpartition('.')[0]))

	def _get_previous_migration_files(self) -> tuple:
		return tuple(map(lambda filename: os.path.join(self.folder, filename), self.sorted_file_list))

	def _get_previous_migrations(self) -> List[dict]:
		migrations = []
		for file in self._get_previous_migration_files():
			with open(file) as f:
				inner = f.read()
				if inner:
					migration = json.loads(inner)
					migrations.append(migration)
		return migrations

	def commit(self, migration: Migration):
		if migration:
			postfix = ".json"
			migration_path = os.path.join(self.folder, str(len(self.sorted_file_list) + 1) + postfix)
			with open(migration_path, 'w+') as migration_file:
				migration_file.write(migration.to_json())

class MigrationEngine:
	def __init__(self, app: App):
		self._app = app

		self.file_manager = MigrationFileManager(app)

	def _build_state(self) -> State:
		state = State(self._app)
		state.build()
		return state

	def _migrate_state(self) -> State:
		state = State(self._app)
		for migration_inner in self.file_manager._get_previous_migrations():
			state.mutate(migration_inner)
		return state

	def get_changes(self) -> Migration:
		prev_state = self._migrate_state()
		state = self._build_state()

		return state.comparer.compare(prev_state)
		
	def migrate(self, executor: BaseExecutor):
		new_migraton = self.get_changes()
		new_migraton.apply(executor)

		self.file_manager.commit(new_migraton)
