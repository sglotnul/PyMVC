from .base import Field, ReadOnlyFieldMixin

class TextField(Field):
	data_type = "TEXT"

class CharField(Field):
	data_type = "VARCHAR(%(max_length)s)"

	def __init__(self, *, max_length=None, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(max_length, int):
			raise Exception("max_leght parameter is required")
		self.data_type %= {'max_length': max_length}

class BooleanField(Field):
	data_type = "BOOL"

class IntegerField(Field):
	data_type = "INTEGER"

class ForeignKey(IntegerField):
	def __init__(self, model, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(model, object):
			raise Exception("argument must be an Model class instance")
		self._model = model.meta.name

	@property
	def meta(self) -> dict:
		return {'references': self._model}

	def deconstruct(self) -> dict:
		meta = super().deconstruct()
		meta['references'] = self._model
		return meta

class PrimaryKeyField(ReadOnlyFieldMixin, IntegerField):
	autoincrement = True

	@property
	def meta(self) -> dict:
		return {'primary_key': True}
