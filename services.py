import json
from typing import List

import utils
from gesture import Gesture


# Añadir un gesto más a los que ya hay en el json
def persist_gesture(gesture: Gesture) -> bool:
    return persist_gestures([gesture])


# Añadir varios gestos a la vez manteniendo los que ya hay en el json
def persist_gestures(gestures: List[Gesture]) -> bool:
    all_gestures = gestures + fetch_gestures()
    ids = [g.id for g in all_gestures]
    ids_set = set(ids)

    # Existen ids repetidas
    if len(ids) != len(ids_set):
        return False

    serializable = [utils.turn_gesture_into_dict(g) for g in all_gestures]

    with open(utils.CONFIG_FILE_NAME, "w") as config_file:
        json.dump(serializable, config_file, indent=4)

    return True


def update_gesture(gesture: Gesture) -> bool:
    list = fetch_gestures()
    old = None
    old_index = -1

    for i, g in enumerate(list):
        if g.id == gesture.id:
            old = g
            old_index = i

    if old is None:
        return False

    list.remove(old)
    list.insert(old_index, gesture)

    serializable = [utils.turn_gesture_into_dict(g) for g in list]

    with open(utils.CONFIG_FILE_NAME, "w") as config_file:
        json.dump(serializable, config_file, indent=4)

    return True


# Gestos de prueba de momento en el futuro sería
# gestos reales con funciones que hagan algo
def fetch_gestures() -> List[Gesture]:
    gestures = []

    with open(utils.CONFIG_FILE_NAME, "r") as config_file:
        gestures = json.load(config_file)

    return [utils.turn_dict_into_gesture(obj) for obj in gestures]
