from typing import Iterable, Tuple
from pafmvc.orm.db.operator import Operator
from pafmvc.orm.db.schema import TableSchemaEngine, FieldSchema, ForeignKeySchema, PrimaryKeySchema

comma = ","

class CreateTableOperator(Operator):
	CREATE = "CREATE {}"
	TABLE = "TABLE {}"
	TEMPORARY = "TEMPORARY {}"
	IF_NOT_EXISTS = "IF NOT EXISTS {}"
	TABLE_TMP = "{} ({})"
	FOREIGN_KEY = "FOREIGN KEY ({field}) REFERENCES {references}({key})"
	PRIMARY_KEY = "PRIMARY KEY ({})"

	def __init__(self):
		self._tables = {}
	
	def _prepare_fields(self, fields: Tuple[FieldSchema]) -> str:
		return comma.join(field.to_sql() for field in fields)
	
	def _prepare_constraints(self, fields: Tuple[FieldSchema]) -> str:
		default_key = "id"
		f_keys = []
		p_key = None
		for field in fields:
			if isinstance(field, ForeignKeySchema):
				f_keys.append(field)
			if isinstance(field, PrimaryKeySchema):
				p_key = field
		constraints = list(self.FOREIGN_KEY.format(field=fk.name, references=fk.references, key=default_key) for fk in f_keys)
		if p_key:
			constraints.append(self.PRIMARY_KEY.format(p_key.name))
		return comma.join(constraints)

	def _prepare_definition(self, fields: Tuple[FieldSchema]) -> str:
		sql_view_fields = self._prepare_fields(fields)
		constraints = self._prepare_constraints(fields)
		if not constraints:
			return sql_view_fields
		return sql_view_fields + comma + constraints

	def _create_single_table_query(self, table: str, data: dict) -> str:
		table_sql_view = self.TABLE_TMP.format(table, self._prepare_definition(data['fields']))
		cmd = self.CREATE
		if data['temporary']:
			cmd = cmd.format(self.TEMPORARY)
		cmd = cmd.format(self.TABLE)
		if data['if_not_exists']:
			cmd = cmd.format(self.IF_NOT_EXISTS)
		return cmd.format(table_sql_view) + ";"

	def set(self, table: str, fields: Iterable[FieldSchema], *, temporary=False, if_not_exists=False):
		self._tables[table] = {
			'fields': tuple(fields),
			'temporary': temporary,
			'if_not_exists': if_not_exists,
		}

	def to_str(self) -> str:
		separator = "\n"
		return separator.join(self._create_single_table_query(table, data) for table, data in self._tables.items())
	
	def __bool__(self) -> bool:
		return bool(self._tables)

class DeleteTableOperator(Operator):
	CMD = "DROP TABLE {};"

	def __init__(self):
		self._tables = []

	def set(self, table: str):
		self._tables.append(table)

	def to_str(self) -> str:
		return self.CMD.format(comma.join(self._tables)) 
	
	def __bool__(self) -> bool:
		return bool(self._tables)

class ChangeTableOperator(Operator):
	def __init__(self):
		self._schemas = []

	def set(self, schema: TableSchemaEngine):
		self._schemas.append(schema)

	def to_str(self) -> str:
		return "\n".join(schema.to_str() for schema in self._schemas)

	def __bool__(self) -> bool:
		return bool(self._schemas)

class AlterTable(Operator):
	CMD = "ALTER TABLE {}"

	def __init__(self):
		self._table = None
	
	def set(self, table: str):
		self._table = table

	def to_str(self) -> str:
		return self.CMD.format(self._table)
	
	def __bool__(self) -> bool:
		return bool(self._table)

class AddOperator(Operator):
	CMD = "ADD {}"

	def __init__(self):
		self._cols = []

	def set(self, field: FieldSchema):
		self._cols.append(field)
	
	def _add_single_field(self, field: FieldSchema) -> str:
		return self.CMD.format(field.to_sql())

	def to_str(self) -> str:
		return comma.join((self._add_single_field(field) for field in self._cols))

	def __bool__(self) -> bool:
		return bool(self._cols)

class DropOperator(Operator):
	CMD = "DROP {}"

	def __init__(self):
		self._cols = []

	def set(self, field: str):
		self._cols.append(field)
	
	def _drop_single_column(self, field: str) -> str:
		return self.CMD.format(field)

	def to_str(self) -> str:
		return comma.join(self._drop_single_column(col) for col in self._cols)

	def __bool__(self) -> bool:
		return bool(self._cols)

class AlterOperator(AddOperator):
	CMD = "CHANGE {}"

class RenameOperator(Operator):
	CMD = "RENAME TO {}"

	def __init__(self):
		self._name = None

	def set(self, name: str):
		self._name = name

	def to_str(self) -> str:
		return self.CMD.format(self._name)

	def __bool__(self) -> bool:
		return bool(self._name)
	
class AddForeignKeyOperator(Operator):
	CMD  = "ADD FOREIGN KEY ({column}) REFERENCES {references}(id)"

	def __init__(self):
		self._foreign_keys = []

	def set(self, field: ForeignKeySchema):
		self._foreign_keys.append(field)

	def _add_single_fk(self, field: ForeignKeySchema) -> str:
		return self.CMD.format(column=field.name, references=field.references)

	def to_str(self) -> str:
		return comma.join((self._add_single_fk(field) for field in self._foreign_keys))
	
	def __bool__(self) -> bool:
		return bool(self._foreign_keys)