from collections import OrderedDict
from abc import ABC, abstractmethod

class Operator(ABC):
	@abstractmethod
	def set(self, *params):
		raise NotImplementedError()

	@abstractmethod
	def __str__(self) -> str:
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

	def __str__(self) -> str:
		postfix = "\n"
		return postfix.join((str(operator) for operator in self._operators.values() if operator))