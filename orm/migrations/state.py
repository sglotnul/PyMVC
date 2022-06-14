from dataclasses import asdict, dataclass, InitVar, field
from typing import Iterable
from mymvc2.apps.app import App
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
	fields: dict = field(init=False)
	raw_fields: InitVar[dict] = None
	meta: InitVar[dict] = None

	def __post_init__(self, raw_fields: dict=None, meta: dict=None):
		super().__post_init__(meta)
		self.fields = {}
		for field, field_data in raw_fields.items():
			self.set_field(field, field_data.pop('data_type'), field_data.pop('default'), field_data.pop('null'), field_data)

	def set_field(self, field: str, data_type: str, default: any, null: bool, meta: dict=None):
		self.fields[field] = FieldState(data_type, default, null, meta)

	def del_field(self, field: str):
		del self.fields[field]

class State:
	def __init__(self, *, migrations: Iterable[Migration]=(), app: App=None):
		self.models = {}

		for migration in migrations:
			migration.apply_to_state(self)

		if app:
			for model in app.get_models():
				fields = dict(map(lambda f: (f.name, f.deconstruct()), model.meta.fields))
				self.set_model(model.meta.name, fields)

	def set_model(self, model: str, fields: dict, meta: dict=None):
		self.models[model] = ModelState(fields, meta)

	def del_model(self, model: str):
		del self.models[model]
