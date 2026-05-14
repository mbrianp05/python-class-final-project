from typing import List

import actions
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
            trigger=lambda path: actions.open_explorer_at(path),  # type: ignore
            param="D:\\Apps",
            settings=data,
        ),
        Gesture(
            name="Abrir editor",
            trigger=lambda exe_path: actions.open_file_with_default_app(exe_path),  # type: ignore
            param="C:\\Users\\user\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Visual Studio Code\\Visual Studio Code",
            settings=data,
        ),
        Gesture(
            name="Subir volumen",
            trigger=lambda delta: actions.set_volume(float(delta)),  # type: ignore
            param="0.2",
            settings=data,
        ),
        Gesture(
            name="Bajar volumen",
            trigger=lambda delta: actions.set_volume(float(delta)),  # type: ignore
            param="-0.2",
            settings=data,
        ),
        Gesture(
            name="Encender wifi",
            trigger=lambda _: actions.set_wifi_state(True),
            param=None,
            settings=data,
        ),
        Gesture(
            name="Apagar wifi",
            trigger=lambda _: actions.set_wifi_state(False),
            param=None,
            settings=data,
        ),
        Gesture(
            name="Reproducir canción",
            trigger=lambda path: actions.open_file_with_default_app(path),  # type: ignore
            param="D:\\Songs\\Metallica - Black Album\\08 - Nothing Else Matters.mp3",
            settings=data,
        ),
        Gesture(
            name="Captura de pantalla",
            trigger=lambda _: actions.take_screenshot(),
            param=None,
            settings=data,
        ),
        Gesture(
            name="Abrir navegador",
            trigger=lambda exe_path: actions.open_file_with_default_app(exe_path),  # type: ignore
            param="C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Google Chrome",
            settings=data,
        ),
    ]
