from dataclasses import dataclass
from typing import Callable


# Cuando el usuario configura un gesto como por ejemplo
# abrir carpeta debe pasar indicar el path de la carpeta como un string
# por ende se crea una instancia de Gesture[str] con "param" con el valor del "path"
@dataclass(frozen=True)
class Gesture[T]:
    name: str
    trigger: Callable[[T], None]
    param: T | None = None
