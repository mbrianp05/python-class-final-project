from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Gesture:
    name: str
    execute: Callable[[], None]
