from typing import Tuple
from mymvc2.orm.db.operator import OperatorRegistry, operator_delegating_metod
from mymvc2.orm.db.query.operators import WhereOperator, SelectOperator
from .operators import *

class DataOperatorRegistry(OperatorRegistry):
	def __init__(self, table: str):
		self._table = table

		super().__init__()

	def to_str(self) -> str:
		query = super().to_str()
		return query and query + ";"

class Inserter(DataOperatorRegistry):
	@operator_delegating_metod
	def insert_from(self, table: str, fields: Tuple[str]=()):
		self._operators['from'].set(table, fields)

	@operator_delegating_metod
	def insert(self, field: str, value: any):
		self._operators['values'].set(field, value)

	def reset(self):
		self._operators['insert'] = InsertIntoOperator()
		self._operators['insert'].set(self._table)
		self._operators['from'] = SelectOperator()
		self._operators['values'] = InsertValuesOperator()

class Remover(DataOperatorRegistry):
	@operator_delegating_metod
	def where(self, *args, **params):
		self._operators['where'].set(params)

	def reset(self):
		self._operators['delete'] = DeleteFromOperator()
		self._operators['delete'].set(self._table)
		self._operators['where'] = WhereOperator()

class Updater(DataOperatorRegistry):
	@operator_delegating_metod
	def set(self, col: str, value: any):
		self._operators['set'].set(col, value)

	@operator_delegating_metod
	def where(self, *args, **params):
		self._operators['where'].set(params)

	def reset(self):
		self._operators['update'] = UpdateOperator()
		self._operators['update'].set(self._table)
		self._operators['set'] = SetOperator()
		self._operators['where'] = WhereOperator()

class DataEngine:
	def insert(self, table: str) -> Inserter:
		return Inserter(table)

	def remove(self, table: str) -> Remover:
		return Remover(table)

	def update(self, table: str) -> Updater:
		return Updater(table)