from dataclasses import dataclass, field, astuple
from typing import Iterable
from pafmvc.apps.app import App

@dataclass	
class FieldState:
	data_type: str
	default: any = field(default=None)
	null: bool = field(default=False)

	def deconstruct(self) -> list:
		return list(astuple(self))

@dataclass
class ModelState:
	fields: dict = field(init=False, default=None)

	def __post_init__(self):
		self.fields = {}

	def set_field(self, field: str, state: FieldState):
		self.fields[field] = state

	def del_field(self, field: str):
		del self.fields[field]

class State:
	def __init__(self, *, migrations: Iterable[object]=(), app: App=None):
		self.models = {}

		for migration in migrations:
			migration.apply_to_state(self)

		if app:
			for model in app.get_models():
				model_state = ModelState()
				self.set_model(model.meta.name, model_state)
				for field in model.meta.fields:
					model_state.set_field(field.name, FieldState(field.data_type, field.default, field.null))

	def set_model(self, model: str, state: ModelState):
		self.models[model] = state

	def del_model(self, model: str):
		del self.models[model]