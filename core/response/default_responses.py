from . import Response

class NotFound(Response):
	def __init__(self):
		super().__init__("404", "<h1>Page Not Found</h1>")

class ServerError(Response):
	def __init__(self):
		super().__init__("500", "<h1>Server Error</h1>")

class MethodNotAllowed(Response):
	def __init__(self):
		super().__init__("405", "<h1>Method Not Allowed</h1>")

PAGES = {
	'404': NotFound(),
	'500': ServerError(),
	'405': MethodNotAllowed(),
}

def get_default_page(code: str=None) -> Response:
	return PAGES.get(code, PAGES['500'])