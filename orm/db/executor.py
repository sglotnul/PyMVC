from abc import ABC, abstractmethod
from .schema import SchemaEngine
from .query import Query
from .entries import DataEngine

class BaseExecutor(ABC):
	schema_engine = SchemaEngine
	query = Query
	data_engine = DataEngine

	def __init__(self, path: str):
		self._path = path

	@abstractmethod
	def connect(self):
		raise NotImplementedError()

	@abstractmethod
	def close(self):
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		raise NotImplementedError()
	
	@abstractmethod
	def rollback(self):
		raise NotImplementedError()
	
	@abstractmethod
	def __call__(self, query: str, *args, script=False):
		raise NotImplementedError()