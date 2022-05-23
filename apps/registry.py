import inspect, sys
from importlib import import_module
from mymvc2.conf.settings import REGISTERED_APPS, BASE_DIR
from .app import App, get_is_exactly_subclass_checker

separator = "."
APP_MODULE_NAME = "apps"

class AppRegistry:
	def __init__(self):
		self.registered_apps = {}

		self.populate()

	def _get_app_config(self, module: str) -> App:
		config = App
		try:
			app_config_module = separator.join((module, APP_MODULE_NAME))
			app_config = import_module(app_config_module)
			configs = inspect.getmembers(app_config, get_is_exactly_subclass_checker(app_config_module, App))
			if configs:
				conf, *others = configs
				if others:
					raise Exception("more than one app config found")
				_, config = conf
		except ModuleNotFoundError:
			raise ModuleNotFoundError(f"{module} app not found")
		return config(module)
		
	def populate(self) -> dict:
		sys.path.insert(0, str(BASE_DIR))
		for module in REGISTERED_APPS:
			config = self._get_app_config(module)
			self.registered_apps[config.app_name] = config
		sys.path.remove(str(BASE_DIR))
		return self.registered_apps

apps = AppRegistry()