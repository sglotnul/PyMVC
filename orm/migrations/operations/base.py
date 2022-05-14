from abc import ABC, abstractmethod, abstractstaticmethod
from mymvc2.orm.db.schema import SchemaEngine

class Operation(ABC):
	def __init__(self, table: str, meta: dict={}):
		self._table = table
		self._meta = meta

	@abstractstaticmethod
	def apply_to_state(state: dict, definition: dict):
		raise NotImplementedError()

	@abstractmethod
	def apply(self, schema: SchemaEngine):
		raise NotImplementedError()

	def deconstruct(self) -> dict:
		base_dict = {"table": self._table}
		base_dict.update(self._meta)
		return base_dict