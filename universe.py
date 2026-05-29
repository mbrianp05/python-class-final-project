import abc
from typing import Any, List

from uiclasses import View
from utilityclasses import Modification

"""
    Un event emmiter nada más que eso XD
"""


class Responder:
    @abc.abstractmethod
    def respond(self, modification: Modification[Any]) -> None:
        """Método para recibir actualizaciones"""


class Navigator:
    @abc.abstractmethod
    def navigate(self, destination: View) -> None:
        """Método para activar una vista"""


class Universe:
    _instance = None

    def __init__(self) -> None:
        self._subscribers: List[Responder] = []
        self._compass: Navigator | None = None

    def responder(self, responder: Responder) -> None:
        self._subscribers.append(responder)

    def signal(
        self, responder: type[Responder], modification: Modification[Any]
    ) -> None:
        for sub in self._subscribers:
            if isinstance(sub, responder):
                sub.respond(modification)
                break

    def navigate(self, destination: View) -> None:
        if self._compass is None:
            return

        self._compass.navigate(destination)

    def compass(self, compass: Navigator) -> None:
        self._compass = compass

    @classmethod
    def rise(cls) -> "Universe":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
