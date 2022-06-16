from abc import ABC, abstractmethod, abstractclassmethod
from pafmvc.orm.db.schema import SchemaEngine

class Operation(ABC):
	def __init__(self, table: str, **meta):
		self._table = table
		self._meta = meta

	@classmethod
	def from_entry(cls, entry: dict) -> object:
		return cls(entry.pop("table"), **entry)

	@abstractmethod
	def apply(self, schema: SchemaEngine):
		raise NotImplementedError()

	@abstractmethod
	def apply_to_state(self, state: object):
		raise NotImplementedError()

	def deconstruct(self) -> dict:
		return {"table": self._table}

	def __bool__(self) -> bool:
		return bool(self._table)