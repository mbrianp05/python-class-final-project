import json
from typing import List

import utils
from gesture import Gesture, GestureData, HandProfile
from utilityclasses import Finger


def mock_gesturedata() -> GestureData:
    return GestureData(
        hands=(True, True),
        visibleFingers=(
            [Finger.THUMB_FINGER, Finger.INDEX_FINGER, Finger.LITTLE_FINGER],
            [],
        ),
        profile=(None, HandProfile.PALM),
    )


# Añadir un gesto más a los que ya hay en el json
def persist_gesture(gesture: Gesture):
    persist_gestures([gesture])


# Añadir varios gestos a la vez manteniendo los que ya hay en el json
def persist_gestures(gestures: List[Gesture]):
    all_gestures = gestures + fetch_gestures()
    serializable = [utils.turn_gesture_into_dict(g) for g in all_gestures]

    with open(utils.CONFIG_FILE_NAME, "w") as config_file:
        json.dump(serializable, config_file, indent=4)


# Gestos de prueba de momento en el futuro sería
# gestos reales con funciones que hagan algo
def fetch_gestures() -> List[Gesture]:
    gestures = []

    with open(utils.CONFIG_FILE_NAME, "r") as config_file:
        gestures = json.load(config_file)

    return [utils.turn_dict_into_gesture(obj) for obj in gestures]
