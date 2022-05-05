from mymvc2.core.response import Response

class NotFound(Response):
	def __init__(self):
		super().__init__("404", "<h1>Page Not Found</h1>")

class ServerError(Response):
	def __init__(self):
		super().__init__("500", "<h1>Server Error</h1>")

PAGES = {
	"404": NotFound(),
	"500": ServerError()
}

def get_default_page(code: str) -> Response:
	return PAGES.get(code, PAGES['500'])