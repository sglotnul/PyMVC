from mymvc2.apps.registry import apps
from mymvc2.core.request import Request
from mymvc2.core.response import Response

class Server:
	def __call__(self, environ: dict, start_response, **kwargs) -> list:
		request = self._get_request(environ)
		view = self._find_view(environ['PATH_INFO'])
		response = self._get_response(request, view)

		return self._start_response(response, start_response)

	def _get_request(self, environ: dict) -> Request:
		return Request(environ)

	def _prepare_url(self, url: str) -> str:
		if url[-1] == '/':
			return url[:-1]
		return url

	def _find_view(self, url: str) -> object:
		url = self._prepare_url(url)
		for app in apps.registered_apps.values():
			for urlpattern in app.get_urlpatterns():
				if urlpattern.path == url:
					return urlpattern.view
		raise Exception("not found")
	
	def _get_response(self, request: Request, view) -> Response:
		response = view(request)
		if not isinstance(response, Response):
			raise Exception("no response")
		return response

	def _start_response(self, response: Response, start_response):
		start_response(str(response.status), response.headers.items())
		return [response.body]
	
def main(environ: dict, start_response, **kwargs):
	s = Server()
	return s(environ, start_response)