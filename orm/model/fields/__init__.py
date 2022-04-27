from mymvc2.orm.model.fields.base import Field, ReadOnlyFieldMixin

class TextField(Field):
	sql_type = "TEXT"

class CharField(Field):
	sql_type = "VARCHAR(%(max_length)s)"

	def __init__(self, *, max_length=None, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(max_length, int):
			raise Exception("max_leght parameter is required")
		self.sql_type %= {'max_length': max_length}

class BooleanField(Field):
	sql_type = "BOOL"

class IntegerField(Field):
	sql_type = "INTEGER"

class ForeignKey(IntegerField):
	def __init__(self, model, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(model, object):
			raise Exception("argument must be an Model class instance")
		self._model = model.__meta__['name']

	def deconstruct(self) -> dict:
		meta = super().deconstruct()
		meta['references'] = self._model
		return meta

class PrimaryKeyField(ReadOnlyFieldMixin, IntegerField):
	autoincrement = True

	def deconstruct(self) -> dict:
		meta = super().deconstruct()
		meta['primary_key'] = True
		return meta
