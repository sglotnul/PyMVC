from pafmvc.core.response.exceptions import ResponseException

class View:
	def get(self, request: object):
		raise ResponseException("405", "get method not allowed")
		
	def post(self, request: object):
		raise ResponseException("405", "post method not allowed")

	def put(self, request: object):
		raise ResponseException("405", "put method not allowed")

	def delete(self, request: object):
		raise ResponseException("405", "delete method not allowed")

	def __call__(self, request) -> object:
		func = getattr(self, request.method)
		return func(request)