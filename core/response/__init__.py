import os
from typing import Tuple
from mymvc2.conf.settings import TEMPLATE_PATH

DEFAULT_HEADERS = {
	"Content-Type": "text/html; charset=utf-8",
	"Content-Length": 0,
}

class Response:
	def __init__(self, status: str, body: bytes, *, headers = {}):
		self.status = status
		if not isinstance(body, bytes):
			body = body.encode('utf-8')
		self.body = body
		
		self._headers = {}

		self.update_headers(DEFAULT_HEADERS)
		self.update_headers(headers)
		self.update_headers({"Content-Length": len(body)})
		
	def update_headers(self, headers: dict):
		self._headers.update(dict(map(lambda entries: (str(entries[0]), str(entries[1])), headers.items())))
	
	def get_headers(self) -> Tuple[Tuple[str]]:
		return tuple(self._headers.items())

def render(template_url: str, context: dict) -> Response:
	with open(os.path.join(TEMPLATE_PATH, template_url), 'rb') as template_io:
		template_bytes = template_io.read()
		return Response('200', template_bytes)

def redirect(url: str) -> Response:
    return Response('301', 'Redirecting...', headers={'Location': url})