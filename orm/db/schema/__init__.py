from mymvc2.orm.db.schema import operators

class TableSchemaEngine(operators.SchemaOperatorRegistry):
	def __init__(self, table: str, fields: dict):
		self._table = table
		self._fields = fields

		super().__init__()

	@operators.operator_delegating_metod
	def add(self, col: str, field_meta: dict):
		if field_meta.get('references'):
			self._operators['add_fk'].set(col, field_meta['references'])
		self._operators['add'].set(col, field_meta)

	@operators.operator_delegating_metod
	def drop(self, col: str):
		self._operators['drop'].set(col)

	@operators.operator_delegating_metod
	def alter(self, col: str, field_meta: dict):
		self._operators['alter'].set(col, field_meta)

	@operators.operator_delegating_metod
	def rename_to(self, to_name: str):
		self._operators['rename_to'].set(to_name)

	@operators.operator_delegating_metod
	def add_foreign_key(self, field: str, to_table: str):
		self._operators['add_fk'].set(field, to_table)

	def copy(self, *, schema: object=None, table: str=None, fields: dict=None) -> object:
		return self.__class__(schema or self._schema, table or self._table, fields or self._fields)
		
	def reset(self):
		self._operators['drop'] = operators.DropOperator(self._table)
		self._operators['add'] = operators.AddOperator(self._table)
		self._operators['alter'] = operators.AlterOperator(self._table)
		self._operators['add_fk'] = operators.AddForeignKeyOperator(self._table)
		self._operators['rename_to'] = operators.RenameOperator(self._table)

class SchemaEngine(operators.SchemaOperatorRegistry):
	@operators.operator_delegating_metod
	def create_table(self, table: str, fields: dict) -> str:
		self._operators['create_table'].set(table, fields)

	@operators.operator_delegating_metod
	def delete_table(self, table: str) -> str:
		self._operators['delete_table'].set(table)

	def alter_table(self, table: str, fields: dict) -> TableSchemaEngine:
		table_schema_engine = TableSchemaEngine(table, fields)
		self._operators['alter_table'].set(table_schema_engine)
		return table_schema_engine
	
	def copy(self) -> object:
		return self.__class__()
	
	def reset(self):
		self._operators['delete_table'] = operators.DeleteTableOperator()
		self._operators['create_table'] = operators.CreateTableOperator()
		self._operators['alter_table'] = operators.ChangeTableOperator()