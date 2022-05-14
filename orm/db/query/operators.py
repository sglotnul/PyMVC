from typing import Tuple
from mymvc2.orm.db.operator import Operator

class SelectOperator(Operator):
	CMD = "SELECT {fields} FROM {table}"
	default = "*"

	def __init__(self):
		self._table = None
		self._fields = ()

	def set(self, table: str, fields: Tuple[str]=[]):
		self._table = table
		self._fields = fields or tuple(self.default)

	def __str__(self) -> str:
		separator = ","
		return self.CMD.format(
			fields = separator.join(self._fields),
			table = self._table
		) 

	def __bool__(self) -> bool:
		return bool(self._table)

class WhereOperator(Operator):
	CMD = "WHERE {}"
	PARAM = "{}=\"{}\""
	AND = " AND "

	def __init__(self):
		self._params = []

	def set(self, params: dict):
		self._params.extend(params.items())

	def __str__(self) -> str:
		return self.CMD.format(self.AND.join((self.PARAM.format(key, value) for key, value in self._params)))

	def __bool__(self) -> bool:
		return bool(len(self._params))

class OrderOperator(Operator):
	CMD = "ORDER BY {field} {ordering}"
	ascending = "ASC"
	descending = "DESC"

	def __init__(self):
		self._field = None

	def _is_descending(self, field: str) -> bool:
		return field.startswith('-')

	def set(self, field: str):
		self._field = field
		self._ordering = self.ascending
		if self._is_descending(field):
			self._field = field[1:]
			self._ordering = self.descending

	def __str__(self) -> str:
		return self.CMD.format(
			field=self._field,
			ordering=self._ordering
		)

	def __bool__(self) -> bool:
		return bool(self._field)

class LimitOperator(Operator):
	CMD = "LIMIT {}"

	def __init__(self):
		self._limit = None

	def set(self, limit: int):
		self._limit = limit

	def __str__(self) -> str:
		return self.CMD.format(self._limit)

	def __bool__(self) -> bool:
		return bool(self._limit is not None)