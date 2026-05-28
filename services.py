import copy
import json
from typing import List

import utils
from gesture import Gesture

# ---------------------------------------------------------------------------
# GestureStore — Singleton con caché de gestos
# ---------------------------------------------------------------------------


class GestureStore:
    """
    Fuente de verdad única para la lista de gestos.

    • La primera llamada a GestureStore.get() lee y parsea el JSON.
    • Las operaciones de escritura (add, update, remove) modifican la caché
      en memoria Y persisten el estado completo al JSON, de forma que ambos
      están siempre sincronizados.
    • Para obtener la instancia: GestureStore.get()
    """

    _instance: "GestureStore | None" = None

    # -- Singleton -----------------------------------------------------------

    @classmethod
    def get(cls) -> "GestureStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -- Inicialización ------------------------------------------------------

    def __init__(self) -> None:
        self._gestures: List[Gesture] = self._load_from_disk()

    # -- Ver sihay gestos ----------------------------------------------------

    def is_empty(self):
        """Mucho mas barato que hacer la comprobación con el método all"""
        return len(self._gestures) == 0

    # -- Lectura -------------------------------------------------------------

    def all(self) -> List[Gesture]:
        """Devuelve una copia de la lista para evitar mutaciones externas."""
        return copy.deepcopy(self._gestures)

    def next_id(self) -> int:
        """Genera el siguiente id disponible (max actual + 1)."""
        if not self._gestures:
            return 1
        return max(g.id for g in self._gestures) + 1

    # -- Escritura -----------------------------------------------------------

    def add(self, gesture: Gesture) -> Gesture:
        """
        Asigna un id definitivo al gesto, lo añade a la caché y persiste.
        Devuelve el gesto con el id asignado.
        """
        gesture = copy.deepcopy(gesture)
        gesture.id = self.next_id()

        self._gestures.append(gesture)
        self._flush()

        return copy.deepcopy(gesture)

    def update(self, gesture: Gesture) -> bool:
        """Reemplaza el gesto con el mismo id. Devuelve False si no existe."""
        index = self._index_of(gesture.id)

        if index == -1:
            return False

        self._gestures[index] = copy.deepcopy(gesture)
        self._flush()

        return True

    def remove(self, gesture: Gesture) -> bool:
        """Elimina el gesto por id. Devuelve False si no existe."""
        index = self._index_of(gesture.id)

        if index == -1:
            return False

        self._gestures.pop(index)
        self._flush()

        return True

    # -- Internals -----------------------------------------------------------

    def _index_of(self, gesture_id: int) -> int:
        for i, g in enumerate(self._gestures):
            if g.id == gesture_id:
                return i

        return -1

    def _load_from_disk(self) -> List[Gesture]:
        with open(utils.CONFIG_FILE_NAME, "r") as f:
            return [utils.turn_dict_into_gesture(obj) for obj in json.load(f)]

    def _flush(self) -> None:
        """Serializa la caché completa al JSON."""
        serializable = [utils.turn_gesture_into_dict(g) for g in self._gestures]
        with open(utils.CONFIG_FILE_NAME, "w") as f:
            json.dump(serializable, f, indent=4)


# ---------------------------------------------------------------------------
# API pública — misma interfaz que antes para no romper las llamadas existentes
# ---------------------------------------------------------------------------


def fetch_gestures() -> List[Gesture]:
    return GestureStore.get().all()


def add_gesture(gesture: Gesture) -> Gesture | None:
    """
    Asigna id definitivo, persiste y devuelve el gesto guardado.
    Devuelve None si el gesto ya tiene un id que colisiona con uno existente.
    """
    store = GestureStore.get()

    if gesture.id != -1 and store._index_of(gesture.id) != -1:
        return None

    return store.add(gesture)


def update_gesture(gesture: Gesture) -> bool:
    return GestureStore.get().update(gesture)


def remove_gesture(gesture: Gesture) -> bool:
    return GestureStore.get().remove(gesture)


# Mantenidas por compatibilidad — delegan en el store
def persist_gesture(gesture: Gesture) -> bool:
    return GestureStore.get().add(gesture) is not None


def persist_gestures(gestures: List[Gesture]) -> bool:
    """Compatibilidad: añade varios gestos a la vez."""
    store = GestureStore.get()
    for g in gestures:
        if store._index_of(g.id) != -1:
            return False  # id duplicado, abortar sin cambios parciales
    for g in gestures:
        store.add(g)
    return True
