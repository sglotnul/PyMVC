class Response:
	headers = {
		"Content-Type": "text/html; charset=utf-8",
		"Content-Length": 0,
	}

	def __init__(self, status, body: str, *, headers = {}):
		self._prepare_headers(headers)
		self._prepare_headers({"Content-Length": str(len(body))})
		
		self.status = status
		self.body = body.encode("utf-8")
		
	def _prepare_headers(self, headers):
		self.headers.update(headers)