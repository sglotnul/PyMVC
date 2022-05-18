from typing import Tuple
from mymvc2.orm.db.query.operators import WhereOperator, SelectOperator
from mymvc2.orm.db.schema.operators import SchemaOperatorRegistry, operator_delegating_metod
from mymvc2.orm.db.entries import operators

class DataOperatorRegistry(SchemaOperatorRegistry):
	def __init__(self, table: str):
		self._table = table

		super().__init__()

	def copy(self) -> object:
		return self.__class__(self._table)

	def __str__(self) -> str:
		query = super().__str__()
		return query and query + ";"

class Inserter(DataOperatorRegistry):
	@operator_delegating_metod
	def insert_from(self, table: str, fields: Tuple[str]=()):
		self._operators['from'].set(table, fields)

	@operator_delegating_metod
	def insert(self, field: str, value: any):
		self._operators['values'].set(field, value)

	def reset(self):
		self._operators['insert'] = operators.InsertIntoOperator()
		self._operators['insert'].set(self._table)
		self._operators['from'] = SelectOperator()
		self._operators['values'] = operators.InsertValuesOperator()

class Remover(DataOperatorRegistry):
	@operator_delegating_metod
	def where(self, *args, **params):
		self._operators['where'].set(params)

	def reset(self):
		self._operators['delete'] = operators.DeleteFromOperator()
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
		self._operators['update'] = operators.UpdateOperator()
		self._operators['update'].set(self._table)
		self._operators['set'] = operators.SetOperator()
		self._operators['where'] = WhereOperator()

class DataEngine:
	def insert(self, table: str) -> Inserter:
		return Inserter(table)

	def remove(self, table: str) -> Remover:
		return Remover(table)

	def update(self, table: str) -> Updater:
		return Updater(table)