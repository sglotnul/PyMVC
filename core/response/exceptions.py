class ResponseException(Exception):
	def __init__(self, code: int, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.code = str(code)
