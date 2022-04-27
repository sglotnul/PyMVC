class SchemaEngine:
	CREATE_TABLE = "CREATE TABLE %(table)s (%(definition)s)"
	DELETE_TABLE = "DROP TABLE %(table)s"

	def create_table(self, table: str, fields: tuple) -> str:
		separator = ","
		context = {
			'table': table,
			'definition': separator.join(fields),
		}
		command = self.CREATE_TABLE % context
		return command

	def delete_table(self, table: str) -> str:
		return self.DELETE_TABLE % {"table": table}
