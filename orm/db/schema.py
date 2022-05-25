from mymvc2.orm.db.operator import OperatorRegistry, Operator, operator_delegating_metod

class TableSchemaEngine(OperatorRegistry):
	def __init__(self, table: str, fields: dict):
		self._table = table
		self._fields = fields

		super().__init__()

	@operator_delegating_metod
	def add(self, col: str, field_meta: dict):
		if field_meta.get('references'):
			self._operators['add_fk'].set(col, field_meta['references'])
		self._operators['add'].set(col, field_meta)

	@operator_delegating_metod
	def drop(self, col: str):
		self._operators['drop'].set(col)

	@operator_delegating_metod
	def alter(self, col: str, field_meta: dict):
		self._operators['alter'].set(col, field_meta)

	@operator_delegating_metod
	def rename_to(self, to_name: str):
		self._operators['rename_to'].set(to_name)

	@operator_delegating_metod
	def add_foreign_key(self, field: str, to_table: str):
		self._operators['add_fk'].set(field, to_table)

	def reset(self):
		self._operators['drop'] = Operator()
		self._operators['add'] = Operator()
		self._operators['alter'] = Operator()
		self._operators['add_fk'] = Operator()
		self._operators['rename_to'] = Operator()

class SchemaEngine(OperatorRegistry):
	@operator_delegating_metod
	def create_table(self, table: str, fields: dict) -> str:
		self._operators['create_table'].set(table, fields)

	@operator_delegating_metod
	def delete_table(self, table: str) -> str:
		self._operators['delete_table'].set(table)

	def alter_table(self, table: str, fields: dict) -> TableSchemaEngine:
		table_schema_engine = TableSchemaEngine(table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine
	
	def reset(self):
		self._operators['delete_table'] = Operator()
		self._operators['create_table'] = Operator()
		self._operators['alter_table'] = Operator()