from typing import List

from gesture import Gesture, GestureData


def mock_gesturedata() -> GestureData:
    return GestureData(
        hands=0,
        visibleFingers=([], []),
    )


# Gestos de prueba de momento en el futuro sería
# gestos reales con funciones que hagan algo
def fetch_gestures() -> List[Gesture]:
    data = mock_gesturedata()

    return [
        Gesture(
            name="Abrir explorador",
            trigger=lambda _: None,
            param=None,
            settings=data,
        ),
        Gesture(name="Abrir editor", trigger=lambda _: None, param=None, settings=data),
        Gesture(
            name="Subir volumen", trigger=lambda _: None, param=None, settings=data
        ),
        Gesture(
            name="Bajar volumen", trigger=lambda _: None, param=None, settings=data
        ),
        Gesture(
            name="Encender wifi", trigger=lambda _: None, param=None, settings=data
        ),
        Gesture(name="Apagar wifi", trigger=lambda _: None, param=None, settings=data),
        Gesture(
            name="Reproducir canción", trigger=lambda _: None, param=None, settings=data
        ),
        Gesture(
            name="Pausar canción", trigger=lambda _: None, param=None, settings=data
        ),
        Gesture(
            name="Abrir navegador", trigger=lambda _: None, param=None, settings=data
        ),
    ]
