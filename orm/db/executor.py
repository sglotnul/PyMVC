from abc import ABC, abstractclassmethod, abstractmethod
from mymvc2.orm.db.schema import SchemaEngine
from mymvc2.orm.db.query import Query
from mymvc2.orm.db.entries import DataEngine

class BaseExecutor(ABC):
	schema_engine = SchemaEngine
	query = Query
	data_engine = DataEngine

	@abstractclassmethod
	def connect(cls):
		raise NotImplementedError()

	@abstractmethod
	def __init__(self, executor):
		raise NotImplementedError()

	@abstractmethod
	def fetch(self):
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		raise NotImplementedError()
	
	@abstractmethod
	def close(self):
		raise NotImplementedError()
	
	@abstractmethod
	def rollback(self):
		raise NotImplementedError()

	@abstractmethod
	def get_lastrowid(self) -> int:
		raise NotImplementedError()
	
	@abstractmethod
	def __call__(self, query: str, *, script=False):
		raise NotImplementedError()
