from dataclasses import asdict, dataclass, InitVar, field
from typing import Iterable
from pafmvc.apps.app import App
from .migration import Migration

@dataclass
class DefaultState:
	def __post_init__(self, meta: dict=None):
		self._meta = meta or {}

	def __getattr__(self, attr: str) -> any:
		meta_value = self._meta.get(attr, None)
		if meta_value is None:
			raise AttributeError(f"{attr} is not defined")
		return meta_value

	def __eq__(self, other: object) -> bool:
		return self.asdict() == other.asdict()

	def asdict(self) -> dict:
		data = asdict(self)
		data.update(self._meta)
		return data

@dataclass	
class FieldState(DefaultState):
	data_type: str
	default: any = field(default=None)
	null: bool = field(default=False)
	meta: InitVar[dict] = None

@dataclass
class ModelState(DefaultState):
	fields: dict = field(init=False, default=None)
	meta: InitVar[dict] = None

	def __post_init__(self, meta: dict=None):
		super().__post_init__(meta)
		self.fields = {}

	def set_field(self, field: str, data_type: str, default: any, null: bool, meta: dict=None) -> FieldState:
		self.fields[field] = FieldState(data_type, default, null, meta)
		return self.fields[field]

	def del_field(self, field: str):
		del self.fields[field]

	def asdict(self) -> dict:
		data = super().asdict()
		data.update({
			'fields': dict((f[0], f[1].asdict()) for f in self.fields.items())
		})
		return data

class State:
	def __init__(self, *, migrations: Iterable[Migration]=(), app: App=None):
		self.models = {}

		for migration in migrations:
			migration.apply_to_state(self)

		if app:
			for model in app.get_models():
				model_state = self.set_model(model.meta.name)
				for field in model.meta.fields:
					model_state.set_field(field.name, field.data_type, field.default, field.null, field.meta)

	def set_model(self, model: str, meta: dict=None) -> ModelState:
		self.models[model] = ModelState(meta)
		return self.models[model]

	def del_model(self, model: str):
		del self.models[model]
