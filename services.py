from typing import List

from gesture import Gesture


# Gestos de prueba de momento en el futuro sería
# gestos reales con funciones que hagan algo
def fetch_gestures() -> List[Gesture]:
    return [
        Gesture(name="Abrir explorador", trigger=lambda _: None),
        Gesture(name="Abrir editor", trigger=lambda _: None),
        Gesture(name="Subir volumen", trigger=lambda _: None),
        Gesture(name="Bajar volumen", trigger=lambda _: None),
        Gesture(name="Encender wifi", trigger=lambda _: None),
        Gesture(name="Apagar wifi", trigger=lambda _: None),
        Gesture(name="Reproducir canción", trigger=lambda _: None),
        Gesture(name="Pausar canción", trigger=lambda _: None),
        Gesture(name="Abrir navegador", trigger=lambda _: None),
    ]
