from inspect import getmembers
from mymvc2.orm.model.fields.base import Field
from mymvc2.orm.model.fields import PrimaryKeyField
from mymvc2.orm.model.manager import Manager

MODEL_META_ATTR = "__meta__"
MANAGER_ATTR = "manager"

class ModelBase(type):
	def __new__(mcs, name, parents, attributes) -> object:
		new_cls = super(ModelBase, mcs).__new__(mcs, name, parents, attributes)

		setattr(new_cls, MANAGER_ATTR, Manager(new_cls))

		fields = tuple(map(lambda i: i[1], getmembers(new_cls, lambda m: isinstance(m, Field))))
		setattr(new_cls, MODEL_META_ATTR, {
			'name': name.lower(),
			'all_fields': fields,
		})

		return new_cls

class Model(metaclass=ModelBase):
	id = PrimaryKeyField()

	def __init__(self, **fields):
		for field in self.__class__.__meta__['all_fields']:
			val = fields.get(field.name)
			if val is None and not field.default:
				raise Exception(f"{field.name} field is reqired")
			field.__set__(self, val)

	def remove(self):
		self.__class__.manager.remove(id=self.id)