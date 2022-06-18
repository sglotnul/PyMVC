class Field:
	data_type = None
	autoincrement = False

	def __init__(self, *, default=None, null=False):
		self.default = default
		self.null = not default and null
	
	@property
	def meta(self) -> dict:
		return {}

	def __set__(self, instance, value):
		instance.__dict__[self.name] = value

	def __get__(self, instance, owner):
		return instance.__dict__.get(self.name, None)

	def __set_name__(self, owner, name):
		self.name = name

class ReadOnlyFieldMixin:
	def __set__(self, instance, value):
		if instance.__dict__.get(self.name, None) is not None:
			raise Exception(f"{self.name} field is read-only")
		instance.__dict__[self.name] = value