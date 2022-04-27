class DataRedactor:
	INSERT = "INSERT INTO %(table)s (%(fields)s) VALUES (%(values)s)"

	def insert(self, table: str, fields: dict) -> str:
		separator = ","
		return self.INSERT % {
			'table': table,
			'fields': separator.join(fields.keys()),
			'values': separator.join(fields.values()),
		}
