from typing import Tuple
from mymvc2.orm.db.operator import OperatorRegistry
from mymvc2.orm.db.query import operators

class Query(OperatorRegistry):
	def __init__(self, table: str, *args, fields: Tuple[str] = None):
		if fields is None:
			fields = []
		self._init_operator = operators.SelectOperator()
		self._init_operator.set(table, fields)
		super().__init__()

	def filter(self, *args, **params):
		self._operators['where'].set(params)

	def order_by(self, field: str):
		self._operators['order_by'].set(field)

	def set_limit(self, limit: int):
		self._operators['limit'].set(limit)

	def reset(self):
		self._operators['where'] = operators.WhereOperator()
		self._operators['order_by'] = operators.OrderOperator()
		self._operators['limit'] = operators.LimitOperator()
	
	def __str__(self) -> str:
		query = super().__str__()
		return query and (str(self._init_operator) + "\n" + query + ";")