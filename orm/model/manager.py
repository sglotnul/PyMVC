from mymvc2.orm.db.connection import connect
from mymvc2.orm.db.query import QuerySet

class Manager:
	def __init__(self, model_cls: type):
		self._model = model_cls

		self._executor = connect()
		self._data_engine = self._executor.data_engine()

	def get_queryset(self):
		return QuerySet(self._model, self._executor)

	def _create_entry(self, query: str) -> int:
		self._executor(query)
		return self._executor.get_lastrowid()

	def create(self, **params):
		fields = {}
		for field in self._model.__meta__['all_fields']:
			if not field.autoincrement:
				val = params.get(field.name, None)
				if val is None:
					raise Exception(f"{field.name} field is reqired")
				fields[field.name] = val
		query = self._data_engine.insert(self._model.__meta__['name'], fields)
		lastrowid = self._create_entry(query)
		return self.get(id=lastrowid)

	def remove(self, **params):
		query = self._data_engine.remove(self._model.__meta__['name'], params)
		self._executor(query)
		self._executor.commit()

	def all(self) -> QuerySet:
		return self.get_queryset()

	def filter(self, **params) -> QuerySet:
		return self.get_queryset().filter(**params)

	def get(self, **params) -> object:
		model = self.get_queryset().get(**params)
		return model

