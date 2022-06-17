import re

class Url:
	def __init__(self, path: str, view: object):
		self._path = path
		self._view = view
	
	def match(self, path: str) -> bool:
		if path[-1] == '/':
			path = path[:-1]
		return re.match(self._path, path)
	
	def get_view(self) -> object:
		return self._view