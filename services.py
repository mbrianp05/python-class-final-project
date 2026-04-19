from typing import List

from gesture import Gesture


# Gestos de prueba de momento en el futuro sería
# gestos reales con funciones que hagan algo
def fetch_gestures() -> List[Gesture]:
    return [
        Gesture(name="Abrir explorador", execute=lambda: None),
        Gesture(name="Abrir editor", execute=lambda: None),
        Gesture(name="Subir volumen", execute=lambda: None),
        Gesture(name="Bajar volumen", execute=lambda: None),
        Gesture(name="Encender wifi", execute=lambda: None),
        Gesture(name="Apagar wifi", execute=lambda: None),
        Gesture(name="Reproducir canción", execute=lambda: None),
        Gesture(name="Pausar canción", execute=lambda: None),
        Gesture(name="Abrir navegador", execute=lambda: None),
    ]
