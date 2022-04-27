from collections import OrderedDict
from typing import List
from abc import abstractmethod
from mymvc2.orm.db.operator import Operator, OperatorRegistry
from mymvc2.orm.model.fields import Field

class QueryOperator(Operator):
	CMD = ""

	@abstractmethod
	def _definition(self) -> dict:
		raise NotImplementedError()

	def __str__(self) -> str:
		return self.CMD % self._definition()

class SelectOperator(QueryOperator):
	CMD = "SELECT %(fields)s FROM %(table)s"
	default = "*"

	def __init__(self, table: str, fields: List[str]):
		self.set(table, fields)

	def set(self, table: str, fields: List[str]):
		self._table = table
		self._fields = fields or list(self.default)

	def _definition(self) -> dict:
		separator = ","
		return {
			'fields': separator.join(self._fields),
			'table': self._table
		}

	def __bool__(self) -> bool:
		return True

class WhereOperator(QueryOperator):
	CMD = "WHERE %(filters)s"
	AND = " AND "
	OR = " OR "

	def __init__(self):
		self._params = []

	def set(self, params: dict):
		self._params.extend(params.items())

	def _definition(self) -> dict:
		separator = self.AND
		return {
			'filters': separator.join((f'{key}={value}' for key, value in self._params))
		}

	def __bool__(self) -> bool:
		return bool(len(self._params))

class OrderOperator(QueryOperator):
	CMD = "ORDER BY %(field)s %(ordering)s"
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
			
	def _definition(self) -> dict:
		return {
			'field': self._field,
			'ordering': self._ordering
		}

	def __bool__(self) -> bool:
		return bool(self._field)

class LimitOperator(QueryOperator):
	CMD = "LIMIT %(limit)s"

	def __init__(self):
		self._limit = None

	def set(self, limit: int):
		self._limit = limit

	def _definition(self) -> dict:
		return {'limit': str(self._limit)}

	def __bool__(self) -> bool:
		return bool(self._limit is not None)

class Query(OperatorRegistry):
	def __init__(self, table: str, *, fields: List[str] = None):
		if fields is None:
			fields = []
		self._table = table 
		self._fields = fields
		super().__init__()

	def filter(self, **params):
		self._operators['where'].set(params)

	def order_by(self, field: str):
		self._operators['order_by'].set(field)

	def set_limit(self, limit: int):
		self._operators['limit'].set(limit)

	def reset(self):
		self._operators['select'] = SelectOperator(self._table, self._fields)
		self._operators['where'] = WhereOperator()
		self._operators['order_by'] = OrderOperator()
		self._operators['limit'] = LimitOperator()

class QuerySet:
	def __init__(self, model_cls: type, executor):
		self._model = model_cls

		self._executor = executor

		self._query = executor.query(model_cls.__meta__['name'])

	def _zip_model(self, row) -> object:
		fields = dict(zip(map(lambda f: f.name, self._model.__meta__['all_fields']), row))
		return self._model(**fields)

	def _get_rows(self) -> object:
		self._executor(str(self._query))
		return self._executor.fetch()

	def _fetch(self) -> List[object]:
		model_list = []
		for row in self._get_rows():
			model_list.append(self._zip_model(row))
		return model_list

	def all(self):
		return self

	def filter(self, **params):
		self._query.filter(**params)
		return self

	def order_by(self, field: str):
		self._query.order_by(field)
		return self

	def get(self, **params) -> object:
		self.filter(**params)
		self._query.set_limit(1)
		rows = tuple(self._get_rows())
		if not rows:
			return None
		return self._zip_model(rows[0])
		
	def __iter__(self):
		for obj in self._fetch():
			yield obj