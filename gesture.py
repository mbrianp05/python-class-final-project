from dataclasses import dataclass
from typing import Callable, List, Literal, Tuple

from utilityclasses import Finger, HandProfile


# En esta clase se guarda toda la data
# relevante que vamos a utilizar para los gestos
# como el numero de manos que aparecen,
# la cantidad de dedos levantados, etc.
@dataclass(frozen=True)
class GestureData:
    hands: Literal[0, 1, 2] = 0
    visibleFingers: Tuple[List[Finger], List[Finger]] = ([], [])
    profile: Tuple[HandProfile, HandProfile] | None = None


# Cuando el usuario configura un gesto como por ejemplo
# abrir carpeta debe pasar indicar el path de la carpeta como un string
# por ende se crea una instancia de Gesture[str] con "param" con el valor del "path"
@dataclass(frozen=True)
class Gesture[T]:
    name: str
    trigger: Callable[[T], None]
    settings: GestureData
    param: T | None = None


# Esta clase se encargara de manejar la logica detectar un gesto
# de forma generica, luego se comparara la data del gesto que el usuario hace
# con la data de los gestos configurados
class GestureRecognition:
    def __init__(self, gestures: List[Gesture]):
        # Data para comparar si hay cambios y entonces ejecutar un nuevo gesto
        self.last_data: GestureData | None = None
        self.current_data: GestureData | None = None

        self.can_do_gesture: bool = True
        self.gestures = gestures

    # Condición necesaria para habilitar
    # la ejecucion de gestos tras un gesto hecho
    # Se analiza el frame y si cunple cierta condicion se
    # vuelve True la prop can_do_gesture
    def __check_to_enable_gestures(self, frame):
        self.can_do_gesture = True

    # Develve la info del frame actual
    # Devuelve None si ninguna de las manos aparecen en la camara
    def __retrieve_gesture_data(self, frame) -> GestureData | None:
        return self.last_data

    # Método principal, se encarga de manejar la lógica de ejecución
    # de los gestos
    def exec_on_detection(self, frame):
        # Llamar a __check_to_enable_gestures si la prop can_do_gesture es True entonces ->
        # Obtener el GestureData info del frame actual con el metood __retrieve_gesture_data
        # Si es diferente a la anterior
        # Buscar en la lista de gestos cual data coincide y ejecutar el primero
        # que encuentre

        # cambiar self.can_do_gesture a False hasta que la condicion necesaria se cumpla

        return self.last_data
