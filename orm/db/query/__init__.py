from typing import Tuple
from mymvc2.orm.db.operator import OperatorRegistry, operator_delegating_metod
from .operators import *

class Query(OperatorRegistry):
	def __init__(self, table: str, *args, fields: Tuple[str] = None):
		if fields is None:
			fields = []
		self._table = table
		self._fields = fields
		super().__init__()

	@operator_delegating_metod
	def filter(self, *args, **params):
		self._operators['where'].set(params)

	@operator_delegating_metod
	def order_by(self, field: str):
		self._operators['order_by'].set(field)

	@operator_delegating_metod
	def set_limit(self, limit: int):
		self._operators['limit'].set(limit)

	def reset(self):
		self._operators['select'] = SelectOperator()
		self._operators['select'].set(self._table, self._fields)
		self._operators['where'] = WhereOperator()
		self._operators['order_by'] = OrderOperator()
		self._operators['limit'] = LimitOperator()
	
	def to_str(self) -> str:
		query = super().to_str()
		return query and query + ";"
