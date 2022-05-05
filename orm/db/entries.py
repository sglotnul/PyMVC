from typing import Tuple
from mymvc2.orm.db.query import WhereOperator

class DataEngine:
	INSERT = "INSERT INTO %(table)s"
	INSERT_VALUES_POSTFIX = "(%(fields)s) VALUES (%(values)s);"
	INSERT_SELECT_FROM_POSTFIX = "SELECT %(fields)s FROM %(from_table)s;"
	DELETE = "DELETE FROM %(table)s %(definition)s;"

	def _insert(self, table: str, postfix: str) -> str:
		separator = " "
		return self.INSERT % {'table': table} + separator + postfix

	def _prepare_tuple(self, t: iter) -> str:
		separator = ","
		return separator.join(t)

	def insert(self, table: str, fields: dict) -> str:
		postfix = self.INSERT_VALUES_POSTFIX % {
			'fields': self._prepare_tuple(fields.keys()),
			'values': self._prepare_tuple(map(lambda val: f"'{val}'", fields.values())),
		}
		return self._insert(table, postfix)

	def insert_from(self, table: str, from_table: str, fields: Tuple[str]) -> str:
		postfix = self.INSERT_SELECT_FROM_POSTFIX % {
			'fields': self._prepare_tuple(fields),
			'from_table': from_table,
		}
		return self._insert(table, postfix)

	def remove(self, table: str, params: dict) -> str:
		operator = WhereOperator()
		operator.set(params)

		return self.DELETE % {
			'table': table,
			'definition': str(operator) if operator else "",
		}