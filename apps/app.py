import inspect, os
from typing import Tuple
from importlib import import_module
from pafmvc.conf.settings import BASE_DIR
from pafmvc.orm.model import Model

MODELS_MODULE = "models"
URLS_MODULE = "urls"
URLPATTERNS = "urlpatterns"
separator = "."

def get_is_exactly_subclass_checker(module: str, cls: object):
	def handler(challenger: any) -> bool:
		return inspect.isclass(challenger) and issubclass(challenger, cls) and challenger.__module__ == module
	return handler

class App:
	app_name = None

	def __init__(self, module: str):
		name = module.rpartition(separator)[2]
		self._module = module
		self._app_name = self.app_name or name
		self._models = ()
		self._urlpatterns = ()

		self.collect_models()
		self.collect_urls()

	def get_models(self) -> Tuple[Model]:
		return self._models

	def get_app_path(self) -> str:
		return os.path.join(BASE_DIR, os.path.join(*self._module.split(separator)))

	def get_urlpatterns(self) -> Tuple[object]:
		return self._urlpatterns

	def collect_models(self):
		try:
			module = separator.join((self._module, MODELS_MODULE))
			models_module = import_module(module)
			self._models = tuple(model for _, model in inspect.getmembers(models_module, get_is_exactly_subclass_checker(module, Model)))
		except ModuleNotFoundError:
			pass
	
	def collect_urls(self):
		try:
			module = separator.join((self._module, URLS_MODULE))
			models_module = import_module(module)
			urlpatterns = getattr(models_module, URLPATTERNS, None)
			if not isinstance(urlpatterns, tuple):
				raise ModuleNotFoundError()
			self._urlpatterns = urlpatterns
		except ModuleNotFoundError:
			pass

