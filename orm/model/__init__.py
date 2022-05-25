from inspect import getmembers
from .fields import PrimaryKeyField
from .manager import Manager
from mymvc2.orm.model.fields.base import Field

PRIVATE_ATTRS = (
	"meta",
	"manager",
)

class ModelBase(type):
	def __new__(mcs, name, parents, attributes) -> object:
		invalid_attrs = tuple(filter(lambda attr: attr in PRIVATE_ATTRS, attributes.keys()))
		if invalid_attrs:
			raise Exception(f"{','.join(invalid_attrs)} are invalid attribute names")

		new_cls = super(ModelBase, mcs).__new__(mcs, name, parents, attributes)

		setattr(new_cls, "manager", Manager(new_cls))

		fields = tuple(map(lambda i: i[1], getmembers(new_cls, lambda m: isinstance(m, Field))))
		setattr(new_cls, "meta", {
			'name': name.lower(),
			'all_fields': fields,
		})

		return new_cls

class Model(metaclass=ModelBase):
	id = PrimaryKeyField()

	def __init__(self, **fields):
		self._state = {}
		self.cls = self.__class__

		for field in self.cls.meta['all_fields']:
			val = fields.get(field.name, None)
			if val is None and not field.null:
				raise Exception(f"{field.name} field is reqired")
			setattr(self, field.name, val)
			self._state[field.name] = val

	def save(self):
		cols = {}
		for field in self.cls.meta['all_fields']:
			val = getattr(self, field.name)
			if val != self._state[field.name]:
				cols[field.name] = val
		if cols:
			self._state.update(cols)
			self.cls.manager.update(cols, id=self.id)
	
	def reset(self):
		self.__dict__.update(self._state)

	def remove(self):
		self.cls.manager.remove(id=self.id)