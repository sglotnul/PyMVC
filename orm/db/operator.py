from collections import OrderedDict
from abc import ABC, abstractmethod

def operator_delegating_metod(func):
	def wrapper(self, *args, **kwargs):
		func(self, *args, **kwargs)
		return self
	return wrapper

class Operator(ABC):
	@abstractmethod
	def set(self, *params):
		raise NotImplementedError()

	@abstractmethod
	def to_str(self) -> str:
		raise NotImplementedError()

	def __bool__(self) -> bool:
		return False

class OperatorRegistry(ABC):
	def __init__(self):
		self._operators = OrderedDict()
		self.reset()

	@abstractmethod
	def reset(self):
		raise NotImplementedError()

	def to_str(self) -> str:
		separator = "\n"
		return separator.join(operator.to_str() for operator in self._operators.values() if operator)