from dataclasses import dataclass
from typing import Callable, Dict, Literal, Tuple

from utilityclasses import Finger, HandProfile


# Cuando el usuario configura un gesto como por ejemplo
# abrir carpeta debe pasar indicar el path de la carpeta como un string
# por ende se crea una instancia de Gesture[str] con "param" con el valor del "path"
@dataclass(frozen=True)
class Gesture[T]:
    name: str
    trigger: Callable[[T], None]
    params: T


# En esta clase se guarda toda la data
# relevante que vamos a utilizar para los gestos
# como el numero de manos que aparecen,
# la cantidad de dedos levantados, etc.
@dataclass(frozen=True)
class GestureData:
    hands: Literal[0, 1, 2]
    visibleFingers: Tuple[Dict[Finger, bool], Dict[Finger, bool]]
    # Creame Propiedad para saber si la mano se ve por la palma, el puño, el lateral
    profile: HandProfile


# Esta clase se encargara de manejar la logica detectar un gesto
# de forma generica, luego se comparara la data del gesto que el usuario hace
# con la data de los gestos configurados
class GestureRecognition:
    def __init__(self):
        pass
