from dataclasses import dataclass
from typing import Tuple
from inspect import getmembers
from .fields import PrimaryKeyField
from .manager import Manager
from pafmvc.orm.model.fields.base import Field

@dataclass
class ModelMeta:
	name: str
	fields: Tuple[Field]

class ModelBase(type):
	def __new__(mcs, name, parents, attributes) -> object:
		new_cls = super(ModelBase, mcs).__new__(mcs, name, parents, attributes)

		setattr(new_cls, "manager", Manager(new_cls))

		fields = tuple(map(lambda i: i[1], getmembers(new_cls, lambda m: isinstance(m, Field))))
		setattr(new_cls, "meta", ModelMeta(name.lower(), fields))

		return new_cls

class Model(metaclass=ModelBase):
	id = PrimaryKeyField()

	def __init__(self, **fields):
		self._state = {}

		for field in self.__class__.meta.fields:
			val = fields.get(field.name, None)
			if val is None and not field.null:
				raise Exception(f"{field.name} field is reqired")
			setattr(self, field.name, val)
			self._state[field.name] = val

	def save(self):
		cols = {}
		for field in self.__class__.meta.fields:
			val = getattr(self, field.name)
			if val != self._state[field.name]:
				cols[field.name] = val
		if cols:
			self._state.update(cols)
			self.__class__.manager.update(cols, id=self.id)
	
	def __operators__(self):
		self.__dict__.update(self._state)

	def remove(self):
		self.__class__.manager.remove(id=self.id)