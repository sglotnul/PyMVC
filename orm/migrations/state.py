from dataclasses import dataclass, field
from typing import Iterable
from pafmvc.apps.app import App
from .migration import Migration

@dataclass	
class FieldState:
	data_type: str
	default: any = field(default=None)
	null: bool = field(default=False)

	def deconstruct(self) -> tuple:
		return (self.data_type, self.default, self.null)

@dataclass
class ModelState:
	fields: dict = field(init=False, default=None)

	def __post_init__(self):
		self.fields = {}

	def set_field(self, field: str, data_type: str, default: any, null: bool) -> FieldState:
		self.fields[field] = FieldState(data_type, default, null)
		return self.fields[field]

	def del_field(self, field: str):
		del self.fields[field]

	def deconstruct(self) -> dict:
		return {
			'fields': tuple(map(lambda f: (f[0], *f[1].deconstruct()), self.fields.items()))
		}

class State:
	def __init__(self, *, migrations: Iterable[Migration]=(), app: App=None):
		self.models = {}

		for migration in migrations:
			migration.apply_to_state(self)

		if app:
			for model in app.get_models():
				model_state = self.set_model(model.meta.name)
				for field in model.meta.fields:
					model_state.set_field(field.name, field.data_type, field.default, field.null)

	def set_model(self, model: str) -> ModelState:
		self.models[model] = ModelState()
		return self.models[model]

	def del_model(self, model: str):
		del self.models[model]
