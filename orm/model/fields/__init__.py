from .base import Field, ReadOnlyFieldMixin

class TextField(Field):
	data_type = "TEXT"

class CharField(Field):
	data_type = "VARCHAR({})"

	def __init__(self, *, max_length=None, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(max_length, int):
			raise Exception("max_leght parameter is required")
		self.data_type = self.data_type.format(max_length)

class BooleanField(Field):
	data_type = "BOOL"

class IntegerField(Field):
	data_type = "INT"

class ForeignKey(Field):
	data_type = "FK({})"

	def __init__(self, model, **kwargs):
		super().__init__(**kwargs)
		if not isinstance(model, object):
			raise Exception("argument must be an Model class instance")
		self._related_model = model.meta.name
		self.data_type = self.data_type.format(self._related_model)

class PrimaryKeyField(ReadOnlyFieldMixin, Field):
	data_type = "PK"
	autoincrement = True

	def __init__(self):
		self.default = None
		self.null = False

class ManyToManyField(ReadOnlyFieldMixin, ForeignKey):
	data_type = "M2M({})"