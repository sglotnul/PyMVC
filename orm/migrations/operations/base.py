from abc import ABC, abstractmethod
from mymvc2.orm.db.schema import SchemaEngine

class Operation(ABC):
	def __init__(self, table: str, meta: dict={}):
		self._table = table
		self._meta = meta
	
	@classmethod 
	def from_entry(cls, entry: dict) -> object:
		table = entry.pop("table")
		return cls(table, entry)

	@abstractmethod
	def apply(self, schema: SchemaEngine):
		raise NotImplementedError()

	@abstractmethod
	def apply_to_state(self, state_dict: dict):
		raise NotImplementedError()

	def deconstruct(self) -> dict:
		base_dict = {"table": self._table}
		base_dict.update(self._meta)
		return base_dict

	def __bool__(self) -> bool:
		return bool(self._table and self._meta)

class SubOperation(Operation):
	def __init__(self, table: str, field: str, meta: dict={}):
		super().__init__(table, meta)
		self._field = field

	def deconstruct(self) -> dict:
		base_dict = {"field": self._field}
		base_dict.update(self._meta)
		return base_dict

	def __bool__(self) -> bool:
		return bool(super().__bool__() and self._field)