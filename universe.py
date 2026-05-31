import abc
from typing import Any, Dict, List

from uiclasses import View
from utilityclasses import Modification

"""
    Un event emmiter nada más que eso XD
"""


class BaseNotifier(abc.ABC):
    @abc.abstractmethod
    def error(self, message: str) -> None:
        """Notificar mensaje de error"""

    @abc.abstractmethod
    def success(self, message: str) -> None:
        """Notificar mensaje de éxito"""


class BaseResponder(abc.ABC):
    @abc.abstractmethod
    def respond(self, modification: Modification[Any]) -> None:
        """Método para recibir actualizaciones"""


class BaseNavigator(abc.ABC):
    @abc.abstractmethod
    def navigate(self, destination: View) -> None:
        """Método para activar una vista"""


class Universe:
    _instance = None

    def __init__(self) -> None:
        self._subscribers: List[BaseResponder] = []
        self._compass: BaseNavigator | None = None
        self._notifiers: Dict[int, BaseNotifier] = {}

    def responder(self, responder: BaseResponder) -> None:
        self._subscribers.append(responder)

    def signal(
        self, responder: type[BaseResponder], modification: Modification[Any]
    ) -> None:
        for sub in self._subscribers:
            if isinstance(sub, responder):
                sub.respond(modification)
                break

    def navigate(self, destination: View) -> None:
        if self._compass is None:
            return

        self._compass.navigate(destination)

    def compass(self, compass: BaseNavigator) -> None:
        self._compass = compass

    def stack_notifier(self, index: int, notifier: BaseNotifier) -> None:
        self._notifiers[index] = notifier

    def notifier(self, index: int) -> BaseNotifier:
        return self._notifiers[index]

    @classmethod
    def rise(cls) -> "Universe":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
