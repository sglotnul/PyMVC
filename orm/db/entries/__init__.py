from typing import Tuple
from mymvc2.orm.db.query.operators import WhereOperator, SelectOperator
from mymvc2.orm.db.schema.operators import SchemaOperatorRegistry, operator_delegating_metod
from mymvc2.orm.db.entries import operators

class Inserter(SchemaOperatorRegistry):
	def __init__(self, table: str):
		self._table = table
		self._init_operator = operators.InsertIntoOperator()
		self._init_operator.set(table)

		super().__init__()

	@operator_delegating_metod
	def insert_from(self, table: str, fields: Tuple[str]=()):
		self._operators['from'].set(table, fields)

	@operator_delegating_metod
	def insert(self, field: str, value: any):
		self._operators['values'].set(field, value)

	def copy(self) -> object:
		return self.__class__(self._table)

	def reset(self):
		self._operators['from'] = SelectOperator()
		self._operators['values'] = operators.InsertValuesOperator()
	
	def __str__(self) -> str:
		query = super().__str__()
		return query and (str(self._init_operator) + "\n" + query + ";")

class Remover(SchemaOperatorRegistry):
	def __init__(self, table: str):
		self._table = table
		self._init_operator = operators.DeleteFromOperator()
		self._init_operator.set(table)

		super().__init__()

	@operator_delegating_metod
	def where(self, *args, **params):
		self._operators['where'].set(params)

	def copy(self) -> object:
		return self.__class__(self._table)

	def reset(self):
		self._operators['where'] = WhereOperator()
	
	def __str__(self) -> str:
		query = super().__str__()
		return query and (str(self._init_operator) + "\n" + query + ";")

class DataEngine:
	def insert(self, table: str) -> Inserter:
		return Inserter(table)

	def remove(self, table: str) -> Remover:
		return Remover(table)